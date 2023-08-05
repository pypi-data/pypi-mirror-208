import os.path
from flask import request, redirect, Response
from urllib.parse import urljoin


class Shortener:
    LINKS_TABLE_NAME = 'short_links'
    CLICKS_TABLE_NAME = 'short_clicks'

    def __init__(self):
        """
        This instance allows you to create short links (random and custom), and use them by clicking on them,

        each click is saved with timestamp, and the Ip address and UserAgent of the clicker (you can choose to not keep the Ip and UserAgent).

        You must init_app() before using it, and pass the required parameters.
        """
        self._app_initialized = False
        self.app = None
        self.db = None
        self._domain = None
        self._rule = None
        self._links_table_name = None
        self._clicks_table_name = None
        self._keep_ip = None
        self._keep_useragent = None
        self.Link = None
        self.Click = None

    def init_app(self, app, db, domain, rule, links_table_name=LINKS_TABLE_NAME, clicks_table_name=CLICKS_TABLE_NAME,
                 keep_ip=True, keep_useragent=True):
        """
        This method initialized the instance with your choosing
        :param app: the running Flask app
        :param db: the database to assign the Models to
        :param domain: your web app domain
        :param rule: the route of the click listener
        :param links_table_name: the name of the links table on the database
        :param clicks_table_name: the name of the clicks table on the database
        :param keep_ip: True to save the Ip address of the clicker, False is not to
        :param keep_useragent: True to save the UserAgent of the clicker, False is not to
        :return: returns this instance (self)
        """
        self.app = app
        self.db = db
        self._domain = domain
        self._rule = rule
        self._links_table_name = links_table_name
        self._clicks_table_name = clicks_table_name
        self._keep_ip = keep_ip
        self._keep_useragent = keep_useragent
        #
        print('(self._domain, self._rule)  ==  ', (self._domain, self._rule))
        endpoint = urljoin(self._domain, self._rule)
        print(f'endpoint passed to init_models: {endpoint}')
        from .models import init_models
        # create the models on the database, and assign them to self.Link and self.Click
        link_model, click_model = init_models(self.db, endpoint, self._links_table_name, self._clicks_table_name, self._keep_ip, self._keep_useragent)
        self.Link = link_model
        self.Click = click_model
        #
        self._define_route()
        #
        self._app_initialized = True  # mark the initialized complete
        #
        return self

    def _assert_initialization(self):
        assert self._app_initialized

    def _new_link(self, url: str, title: str, uid: str, _add_to_session=True, **kwargs):
        """
        This method creates new Link model with entered values, and returns it.
        :param url: the long URL you want to shorten
        :param title: Optional title for the URL
        :param uid: the unique generated uid for this Link
        :param _add_to_session: Optional to add it to the session
        :param kwargs: values for the extra columns (col_name=value)
        :return: Link model object (instance)
        """
        self._assert_initialization()  # error if not self._app_initialized
        new_link = self.Link()
        new_link.url = url
        new_link.title = title
        new_link.uid = uid
        # setting the extra columns
        for key, value in kwargs.items():
            setattr(new_link, key, value)
        #
        if _add_to_session:
            self.db.session.add(new_link)
        return new_link

    def shorten(self, url: str, title: str = None, _length: int = 2, _commit=False, **kwargs):
        """
        Makes new random shortened url, and adds it to the db session,

        you can set _commit to True to commit!
        :param url: the URL you want to shorten
        :param title: Optional title
        :param _length: the minimum length of shortened url uid
        :param _commit: to auto commit, False by default
        :param kwargs: these are the extra columns you manually added, you can set them values with this kwargs
        :return: Link instance
        """
        self._assert_initialization()  # error if not self._app_initialized
        from .methods import create_random_new_unique_uid
        uids_set = {l.uid for l in self.Link.query.all()}
        uid = create_random_new_unique_uid(_length, uids_list=uids_set)
        new_link = self._new_link(url, title, uid, _add_to_session=True, **kwargs)
        if _commit:
            self.db.session.commit()
        return new_link

    def custom_shorten(self, url: str, title: str = None, _custom: str = 'custom', _append_to_custom: bool = True, _sep: str = None, _commit=False, **kwargs):
        """
        Makes new custom shortened url, and adds it to the db session,

        you can set _commit to True to commit!
        :param url: the URL you want to shorten
        :param title: Optional title
        :param _custom: The Custom signature you want to assign to the uid
        :param _append_to_custom: to allow appending to the custom signature
        :param _sep: a separator between the signature and the random token
        :param _commit: to auto commit, False by default
        :param kwargs: these are the extra columns you manually added, you can set them values with this kwargs
        :return: Link instance
        """
        self._assert_initialization()  # error if not self._app_initialized
        from .methods import create_custom_new_uid
        uids_set = {l.uid for l in self.Link.query.all()}
        uid = create_custom_new_uid(uids_set, _custom, _append_to_custom, _sep)
        new_link = self._new_link(url, title, uid, _add_to_session=True, **kwargs)
        if _commit:
            self.db.session.commit()
        return new_link

    def _uid_not_found_action(self, uid: str):
        """
        currently, this action just rises an error
        :param uid: the uid that doesn't exist
        :return: None
        """
        raise ValueError(f'Uid is not found "{uid}"')

    def _make_click(self, link_object, ip, useragent):
        """
        this method creates a Click object for $link_object
        :param link_object: the ORM Link model
        :param ip: True to save the `flask.request.remote_addr`, False not to save
        :param useragent: True to save the `flask.request.user_agent.string`, False not to save
        :return: the Click model object (instance)
        """
        self._assert_initialization()  # error if not self._app_initialized
        clk = self.Click()
        clk.link = link_object
        if ip:
            clk.ip = request.remote_addr
        if useragent:
            clk.user_agent = request.user_agent.string
        return clk

    def click(self, uid: str, keep_ip: bool = None, keep_useragent: bool = None) -> Response:
        """
        Marks the click and returns a redirection response to the destination
        :param uid: the short url uid to click
        :param keep_ip: you can choose to override the default option
        :param keep_useragent: you can choose to override the default option
        :return: Redirection Response
        """
        self._assert_initialization()  # error if not self._app_initialized
        target = self.Link.query.filter_by(uid=uid).first()  # query the Link with $uid
        if not target:  # check and proceed with error action if not exists
            self._uid_not_found_action(uid)
        # > This else statement is here in case self._uid_not_found_action didn't raise error, we have to escape this code
        else:
            # > override the default option if one is input
            if keep_ip is None:
                keep_ip = self._keep_ip
            if keep_useragent is None:
                keep_useragent = self._keep_useragent
            # > make the Click model for this click
            click = self._make_click(target, keep_ip, keep_useragent)
            # > clicks are added to session and committed automatically
            self.db.session.add(click)
            self.db.session.commit()
            # > redirect to the destination URL
            return redirect(target.url)

    def _define_route(self):
        """
        This method registers a route on the flask app for this extension
        :return:
        """
        route = os.path.join(self._rule, '<string:uid>')

        @self.app.route(route)
        def url_click_listener(uid: str):
            return self.click(uid)
