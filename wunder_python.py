"""z_wunderpy is a Wunderlist API driver for python, designed by
Nicholas Zufelt.

To use it, construct an object with an oauth_token and a client_id as:

>>> import z_wunderpy
>>> nick = Wunder(oauth_token = "USER_OAUTH_TOKEN", client_id= "CLIENT_ID")

You're then ready to take actions on nick's account, such as:

>>> nick.get_user()
{'updated_at': '2016-01-13T06:39:44.372Z', 'id': NNNNNNNN,
'created_at': '2015-11-04T09:52:38.550Z', 'revision': 216,
'email': 'example@email.com', 'name': 'Nicholas Zufelt',
'type': 'user'}

In our example (and all the examples in the docstrings of the various
methods), we named the object `nick`.  This reflects the ideology
that a Wunder object is connected to a single user's Wunderlist account.
If you want to access multiple users, you should create a Wunder object
for each user.  They'll need to authorize your app to access their
Wunderlist account using OAuth.  This is much easier to accomplish if
you only want to access your own account (so don't be frightened by OAuth,
as I originally was!).  To reiterate: the client_id is Wunderlist's reference
to your app, and oauth_token is the token used by you to access a specific
user's account.

Endpoints on the WL API Docs:
Avatar -- TODO
File -- TODO
File preview -- TODO
Folder -- Done
List -- Done
Membership -- TODO
Note -- Done
Positions -- TODO
Reminder -- TODO
Root -- TODO
Subtask -- Done
Task -- Done
Task comment -- TODO
Upload -- TODO
User -- Done
Webhooks -- TODO
"""

import json
import requests

class Wunder(object): #pylint: disable=R0904
    """ An object used to access the Wunderlist API.  It is created
    with an `oauth_token` and a `client_id`.  Thus, you should treat it as
    one user's Wunderlist data, because that's all it can access (as
    different users would have different oauth_tokens).

    I do not guarantee that this is the best, nor even a good, way to
    handle the security requirements of users' oauth_tokens.  Use at
    your own risk.
    """
    def __init__(self, oauth_token, client_id):
        """ Instantiate and return a Wunder Object with all the
        headers it will need.
        """
        self.headers_plain = {'X-Access-Token': oauth_token,
                              'X-Client-ID': client_id}
        self.headers_payload = {'X-Access-Token': oauth_token,
                                'X-Client-ID': client_id,
                                'Content-Type':'application/json'}

    def _get(self, url, **kwargs):
        """ Perform a GET request on `url`.

        The resulting Response object
        contains a json() format of the content which is the useful
        object for Wunder's methods.  The content of this object is a
        dict or a list of dicts, and this is returned.  That is, the
        Response object is hidden from the user, because they don't
        need anything else it provides.

        Parameters:
        url -- the url at which to GET

        Optional keyword arguments:
        payload -- a dict of data to be sent along with the GET request,
        params -- a dict of parameters to pass to the url
        """
        if 'payload' in kwargs:
            kwargs['data'] = json.dumps(kwargs['payload'])
            del kwargs['payload']
            kwargs['headers'] = self.headers_payload
        else:
            kwargs['headers'] = self.headers_plain

        response = requests.get(url, **kwargs)
        self._check_response(response)
        return response.json()

    def _post(self, url, **kwargs):
        """Perform a POST request on `url`.

        The resulting Response object
        contains a json() format of the content which is the useful
        object for Wunder's methods.  The content of this object is a
        dict or a list of dicts, and this is returned.  That is, the
        Response object is hidden from the user, because they don't
        need anything else it provides.

        Parameters:
        url -- the url at which to POST

        Optional keyword arguments:
        payload -- a dict of data to be sent along with the POST request,
        params -- a dict of parameters to pass to the url
        """
        if 'payload' in kwargs:
            kwargs['data'] = json.dumps(kwargs['payload'])
            del kwargs['payload']
            kwargs['headers'] = self.headers_payload
        else:
            kwargs['headers'] = self.headers_plain

        response = requests.post(url, **kwargs)
        self._check_response(response)
        return response.json()

    def _patch(self, url, payload):
        """Perform a PATCH request on `url`.

        The resulting Response object
        contains a json() format of the content which is the useful
        object for Wunder's methods.  The content of this object is a
        dict or a list of dicts, and this is returned.  That is, the
        Response object is hidden from the user, because they don't
        need anything else it provides.

        Parameters:
        url -- the url at which to PATCH
        payload -- a dict of data to be sent along with the PATCH request

        Optional keyword arguments:
        params -- a dict of parameters to pass to the url
        """

        response = requests.patch(url, data=json.dumps(payload),
                                  headers=self.headers_payload)
        self._check_response(response)
        return response.json()

    def _delete(self, url, **kwargs):
        """
        Performs a DELETE request on `url`.

        Parameters:
        url -- the url at which to DELETE

        Optional keyword arguments:
        payload -- a dict of data to be sent along with the DELETE request,
        params -- a dict of parameters to pass to the url

        Return:
        boolean of success.
        """

        if 'payload' in kwargs:
            kwargs['data'] = json.dumps(kwargs['payload'])
            del kwargs['payload']
            kwargs['headers'] = self.headers_payload
        else:
            kwargs['headers'] = self.headers_plain

        response = requests.delete(url, **kwargs)
        self._check_response(response)
        return response.status_code == 204

    @staticmethod
    def _check_title(title):
        """ Raise an error if the given title is too long.

        The Wunderlist API requires that titles be 255 characters or fewer.

        Parameters:
        title -- string
        """
        if len(title) > 255:
            raise ValueError('Title is too long (255 char max).')

    @staticmethod
    def _check_response(response):
        """ Check the response from _get, _post, _patch, and _delete to
        see if there were errors from the api, and raise them as exceptions.
        """
        jres = response.json()
        if isinstance(jres, list):
            # Definitely not an error response!
            return
        if 'error' in jres.keys():
            if 'revision_conflict' in jres['error']:
                raise ValueError("Revision number is incorrect.")
            else:
                # All others that I've found have descriptive messages
                raise ValueError(jres['error']['message'])

    #### USER METHODS ####
    def get_user(self):
        """Get the current user."""
        return self._get('https://a.wunderlist.com/api/v1/user')

    def get_users(self, list_id=None):
        """ Get all users the current user has access to.

        With a `list_id` included, restricts to those users with access to
        the given list.  As of February 2016, this feature is bugged, my
        response object is giving me garbage back.

        Optional keyword arguments:
        list_id -- restrict response to only a specific list.

        Return:
        list of dicts detailing users
        """
        url = 'http://a.wunderlist.com/api/v1/users'
        if list_id is not None:
            params = {'list_id':list_id}
            users = self._get(url, params=params)
        else:
            users = self._get(url)

        return users

    #### LIST METHODS ####
    def get_lists(self):
        """Get all lists."""
        return self._get('https://a.wunderlist.com/api/v1/lists')

    def get_list(self, list_id):
        """ Get a list with the given `list_id`."""
        return self._get('https://a.wunderlist.com/api/v1/lists/'
                         + str(list_id))

    def update_list(self, list_id, **kwargs):
        """ Update a list with the given information.

        As of the latest version of Wunderlist, the only thing that can be
        updated on a list is its title, and so the one would call this as:

        >>> nick.update_list(list_id,title = 'My New Title')

        The PATCH call that update_list() is based upon requires that
        the revision number be accurate, otherwise it will raise a ValueError.
        If you do not include revision as a kwarg, then update_list() will
        fetch it for you (though it is probably best practice to minimize
        API requests).

        Parameters:
        list_id -- the id of the list to update

        Optional keyword arguments:
        revision -- the revision number of the current request.
        title -- the new title for the list.  Note that while title
            isn't required, it is currently the only functionality this
            method offers.

        Return:
        dict of new list details
        """
        if 'title' in kwargs:
            # It should always be.
            self._check_title(kwargs['title'])
        if 'revision' not in kwargs:
            kwargs['revision'] = self.list_revision(list_id)
        url = 'http://a.wunderlist.com/api/v1/lists/' + str(list_id)
        return self._patch(url, payload=kwargs)

    def make_list(self, title):
        """Create a new list.

        Parameters:
        title -- string of new title

        Return:
        dict of new list details
        """
        self._check_title(title)
        payload = {'title':str(title)}
        url = 'http://a.wunderlist.com/api/v1/lists'

        return self._post(url, payload=payload)

    def make_list_public(self, list_id, revision=None):
        """ Make a list public.

        I suspect this API call is depreciated, because public lists are
        depreciated.  I think in the future they will make a
        comeback, but I added this functionality anyways. As a
        result, I haven't tested this for correctness (I don't know that
        it's possible to do so at this time).

        Parameters:
        list_id -- The list to make public.

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        payload = {'public':True}
        if revision is not None:
            payload['revision'] = revision

        url = 'http://a.wunderlist.com/api/v1/lists/' + str(list_id)

        is_public = self._patch(url, payload=payload)

        return is_public['public'] == "true"

    def delete_list(self, list_id, revision=None):
        """ Delete a list.

        Parameters:
        list_id -- int list_id to be deleted

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        params = {}

        if revision is None:
            params['revision'] = self.list_revision(list_id)
        else:
            params['revision'] = revision

        url = 'http://a.wunderlist.com/api/v1/lists/' + str(list_id)
        return self._delete(url, params=params)

    #### FOLDER METHODS ####
    def get_folders(self):
        """Get all folders."""
        url = 'http://a.wunderlist.com/api/v1/folders'
        return self._get(url)

    def get_folder(self, folder_id):
        """ Get a single folder."""
        url = 'http://a.wunderlist.com/api/v1/folders/'+str(folder_id)
        return self._get(url)

    def make_folder(self, title, list_ids):
        """ Create a new folder which contains the lists given in
        `list_ids`.

        To determine the list_id of a list you want to add to the
        folder, use get_list_ids().

        Parameters:
        title -- string, title of new folder.
        list_ids -- list of ints, the collection of list_ids to add to folder.

        Return:
        dict of new folder details
        """
        self._check_title(title)
        payload = {"title": title, "list_ids": list_ids}
        url = 'http://a.wunderlist.com/api/v1/folders'
        return self._post(url, payload=payload)

    def get_folder_revisions(self):
        """ Get all folder revisions.

        An example return would be the following:

        [{'id': 0000001, 'revision': 6, 'type': 'folder_revision'},
        {'id': 0000002, 'revision': 9, 'type': 'folder_revision'},
        {'id': 0000003, 'revision': 40, 'type': 'folder_revision'},
        {'id': 0000004, 'revision': 10, 'type': 'folder_revision'}]

        Return:
        list of dicts containing folder_ids and their revision.
        """
        url = 'http://a.wunderlist.com/api/v1/folder_revisions'
        return self._get(url)

    def update_folder(self, folder_id, **kwargs):
        """ Change either the title or the members of a folder.

        To change the title, call with:
        >>> nick.update_folder(folder_id,title='new_title_name')

        To change (list) members, call with:
        >>> nick.update_folder(folder_id,list_ids=[list_id1,...])

        Note that this will replace the lists in the folder. To add a list
        to a folder, use the convenience function `add_to_folder()`.

        The PATCH call that update_folder() is based upon requires that
        the revision number be accurate, otherwise it will raise a ValueError.
        If you do not include revision as a kwarg, then update_folder() will
        fetch it for you (though it is probably best practice to minimize
        API requests).

        Parameters:
        folder_id -- the id of the folder to be updated

        Optional keyword arguments:
        revision -- the revision number of the current request.
        title -- include to change the title of the folder
        list_ids -- a list of ints, list_ids to change members

        Return:
        dict of new folder details
        """
        if 'title' in kwargs:
            self._check_title(kwargs['title'])
        if 'revision' not in kwargs:
            kwargs['revision'] = self.folder_revision(folder_id)
        url = 'http://a.wunderlist.com/api/v1/folders/'+str(folder_id)
        return self._patch(url, payload=kwargs)

    def delete_folder(self, folder_id, revision=None):
        """ Delete a folder.

        Note that deleting a folder does not delete the lists contained
        therein.

        Parameters:
        folder_id -- the id of the folder to be deleted

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        if revision is None:
            revision = self.folder_revision(folder_id)

        url = 'http://a.wunderlist.com/api/v1/folders/'+str(folder_id)
        return self._delete(url, params={'revision': str(revision)})

    #### TASK METHODS ####
    def get_tasks(self, list_id, completed=False):
        """Get all tasks from a list.

        To get completed tasks, include `completed = True`.

        Parameters:
        list_id -- the id of the list containing the desired tasks.

        Optional keyword arguments:
        completed -- boolean (default = False), with True will return only
            completed tasks.

        Return:
        list of tasks (dicts)
        """
        params = {'list_id': list_id, 'completed': completed}
        url = 'http://a.wunderlist.com/api/v1/tasks'
        return self._get(url, params=params)

    def get_task(self, task_id):
        """Get a specific task."""
        url = 'http://a.wunderlist.com/api/v1/tasks/' + str(task_id)
        return self._get(url)

    def make_task(self, list_id, title, **kwargs):
        """ Create a task.

        Parameters:
        name -- string of new title

        Optional keyword arguments:
        assignee_id -- int
        completed -- boolean
        recurrence_type -- string,  Valid options:
            "day", "week", "month", "year",
            must be accompanied by recurrence_count
        recurrence_count -- integer, must be >= 1, must be accompanied
            by recurrence_type
        due_date -- string, formatted as an ISO8601 date
        starred -- boolean

        Return:
        dict of task details
        """
        self._check_title(title)
        payload = {'list_id' : list_id, 'title' : title}
        payload.update(kwargs)
        url = 'https://a.wunderlist.com/api/v1/tasks'
        return self._post(url, payload=payload)

    def update_task(self, task_id, **kwargs):
        """ Update a task.

        The PATCH call that update_task() is based upon requires that
        the revision number be accurate, otherwise it will raise a ValueError.
        If you do not include revision as a kwarg, then update_task() will
        fetch it for you (though it is probably best practice to minimize
        API requests).

        Parameters:
        task_id -- the id of the task to be updated

        Optional keyword arguments:
        revision -- the revision number of the current request.
        title -- string
        assignee_id -- int
        completed -- boolean
        recurrence_type -- string,  Valid options:
            "day", "week", "month", "year",
            must be accompanied by recurrence_count
        recurrence_count -- integer, must be >= 1, must be accompanied
            by recurrence_type
        due_date -- string, formatted as an ISO8601 date
        starred -- boolean
        remove -- list of strings, a list of attributes to delete from
            the task, e.g. 'due_date'

        Return:
        dict of new task details
        """
        if 'title' in kwargs:
            self._check_title(kwargs['title'])
        if 'revision' not in kwargs:
            kwargs['revision'] = self.get_task(task_id)['revision']
        url = 'http://a.wunderlist.com/api/v1/tasks/' + str(task_id)
        return self._patch(url, payload=kwargs)

    def delete_task(self, task_id, revision=None):
        """ Delete a task.

        Parameters:
        task_id -- the id of the task to be updated

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        if revision is None:
            revision = self.get_task(task_id=task_id)['revision']
        url = 'http://a.wunderlist.com/api/v1/tasks/'+str(task_id)
        return self._delete(url, params={'revision': str(revision)})

    #### Subtask Methods
    def get_subtasks(self, list_id=None, task_id=None, completed=False):
        """ Get all subtasks for either a list or a task.

        Optional keyword arguments (Note exactly one of `task_id` or
            `list_id` is required):
        list_id -- The list from which to get all subtasks
        task_id -- The task from which to get all subtasks
        completed -- if True, return only the completed subtasks

        Return:
        list of dicts describing each subtask
        """
        if list_id is None and task_id is None:
            raise TypeError('get_subtasks requires exactly one of list_id or task_id.')
        elif task_id is None:
            params = {'list_id':list_id}
        elif list_id is None:
            params = {'task_id':task_id}
        else:
            raise TypeError('get_subtasks requires exactly one of list_id or task_id.')
        if completed:
            params['completed'] = True

        url = 'http://a.wunderlist.com/api/v1/subtasks'
        return self._get(url, params=params)

    def get_subtask(self, subtask_id):
        """ Get a subtask with the given `subtask_id`."""
        return self._get('https://a.wunderlist.com/api/v1/subtasks/'
                         + str(subtask_id))

    def make_subtask(self, task_id, title, completed=False):
        """ Create a subtask.

        Parameters:
        task_id -- int, id of parent task
        name -- string of new title

        Optional keyword arguments:
        completed -- boolean

        Return:
        dict of subtask details
        """
        self._check_title(title)
        payload = {'task_id': task_id, 'title': title}
        if completed:
            payload['completed'] = True
        url = 'https://a.wunderlist.com/api/v1/subtasks'
        return self._post(url, payload=payload)

    def update_subtask(self, subtask_id, **kwargs):
        """ Update a subtask.

        The PATCH call that update_subtask() is based upon requires that
        the revision number be accurate, otherwise it will raise a ValueError.
        If you do not include revision as a kwarg, then update_subtask() will
        fetch it for you (though it is probably best practice to minimize
        API requests).

        Parameters:
        subtask_id -- the id of the task to be updated

        Optional keyword arguments:
        revision -- the revision number of the current request.
        title -- string
        completed -- boolean

        Return:
        dict of new subtask details
        """
        if 'title' in kwargs:
            self._check_title(kwargs['title'])
        if 'revision' not in kwargs:
            kwargs['revision'] = self.get_subtask(subtask_id)['revision']
        url = 'http://a.wunderlist.com/api/v1/subtasks/' + str(subtask_id)
        return self._patch(url, payload=kwargs)

    def delete_subtask(self, subtask_id, revision=None):
        """ Delete a subtask.

        Parameters:
        subtask_id -- the id of the subtask to be delete

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        if revision is None:
            revision = self.get_subtask(subtask_id)['revision']
        url = 'http://a.wunderlist.com/api/v1/subtasks/'+str(subtask_id)
        return self._delete(url, params={'revision': revision})

    #### Note Methods
    def get_notes(self, list_id=None, task_id=None):
        """ Get all notes for either a list or a task.

        Observe that tasks can only have one note attached to them, but
        they still return a list of dicts.  Perhaps multiple notes
        will be allowed in the future.  This means you will need to add
        `[0]` to your calls where you may not think you need to.

        Optional keyword arguments (Exactly one is required):
        list_id -- The list from which to get all notes
        task_id -- The task from which to get all notes

        Return:
        list of dicts describing each note
        """
        if list_id is None and task_id is None:
            raise TypeError('get_notes requires exactly one of list_id or task_id.')
        elif task_id is None:
            params = {'list_id':list_id}
        elif list_id is None:
            params = {'task_id':task_id}
        else:
            raise TypeError('get_notes requires exactly one of list_id or task_id.')

        url = 'http://a.wunderlist.com/api/v1/notes'
        return self._get(url, params=params)

    def get_note(self, note_id):
        """ Get a note.

        Observe that each task can only have one note, so you may wish to
        call this with a `task_id`, rather than a `note_id`.  To do so, use
        the helper function `get_note_id`, which takes a `task_id`:
        >>> nick.get_note(nick.get_note_id(task_id))
        """
        return self._get('https://a.wunderlist.com/api/v1/notes/'
                         + str(note_id))

    def make_note(self, task_id, content):
        """ Create a note in the task specified by `task_id`.

        Parameters:
        task_id -- int
        content -- string, content of new note

        Return:
        dict of note details
        """
        payload = {'task_id': task_id, 'content': content}
        url = 'https://a.wunderlist.com/api/v1/notes'
        return self._post(url, payload=payload)

    def update_note(self, note_id, content, revision=None):
        """ Update a note.

        The PATCH call that update_note() is based upon requires that
        the revision number be accurate, otherwise it will raise a ValueError.
        If you do not include revision as a kwarg, then update_note() will
        fetch it for you (though it is probably best practice to minimize
        API requests).

        Observe that each task can only have one note, so you may wish to
        call this with a `task_id`, rather than a `note_id`.  To do so, use
        the helper function `get_note_id`, which takes a `task_id`:
        >>> nick.update_note(nick.get_note_id(task_id), content)

        Parameters:
        note_id -- the id of the task to be updated
        content -- string

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        dict of new note details
        """
        if revision is None:
            revision = self.get_note(note_id)['revision']
        payload = {'revision': revision, 'content': content}
        url = 'http://a.wunderlist.com/api/v1/notes/' + str(note_id)
        return self._patch(url, payload=payload)

    def delete_note(self, note_id, revision=None):
        """ Delete a note from a task.

        Observe that each task can only have one note, so you may wish to
        call this with a `task_id`, rather than a `note_id`.  To do so, use
        the helper function `get_note_id`, which takes a `task_id`:
        >>> nick.delete_note(nick.get_note_id(task_id))

        Parameters:
        note_id -- the id of the note to be deleted

        Optional keyword arguments:
        revision -- the revision number of the current request.

        Return:
        boolean of success
        """
        if revision is None:
            revision = self.get_note(note_id)['revision']
        url = 'http://a.wunderlist.com/api/v1/notes/'+str(note_id)
        return self._delete(url, params={'revision': revision})

    #### Special Methods
    # The following were created to be of additional help, and are not
    # directly associated to an API call.
    def list_ids(self, title=None):
        """Return a dict containing title: list_id pairs.
        Useful to quickly grab a list_id in another method call, as:

        >>> nick.make_task(nick.list_ids()['My List Name'],
                           title='iPhone charger')
        OR

        >>> nick.make_task(nick.list_ids('My List Name'),
                           title='iPhone charger')

        Optional keyword arguments (Note exactly one is required):
        title - string, name of title to return the list_id

        Return:

        """
        list_ids = {}
        for zlist in self.get_lists():
            list_ids[zlist['title']] = zlist['id']
        if title is not None:
            return list_ids[title]
        return list_ids

    def list_revision(self, list_id):
        """ Fetch the current list revision. To avoid making
        too many calls to the API, you may want to store revisions
        (these are part of the returned object to any of these API
        calls.)  However, if you don't have the correct revision,
        the respose will fail, so be ready to catch that exception
        and call this method again.
        """
        return self.get_list(list_id)['revision']

    def folder_ids(self):
        """Return a dict containing title: folder_id pairs.
        Useful to quickly grab a folder_id in another method call.
        """

        folder_ids = {}
        for folder in self.get_folders():
            folder_ids[folder['title']] = folder['id']
        return folder_ids

    def folder_revision(self, folder_id):
        """ Fetch the current folder revision. To avoid making
        too many calls to the API, you may want to store revisions
        (these are part of the returned object to any of these API
        calls.)  However, if you don't have the correct revision,
        the respose will fail, so be ready to catch that exception
        and call this method again.
        """
        return self.get_folder(folder_id)['revision']

    def add_to_folder(self, list_id, folder_id):
        """ Add list with list_id to folder.  This method is idempotent.
        """
        list_ids = self.get_folder(folder_id)['list_ids']
        if list_id not in list_ids:
            list_ids.append(list_id)
        folder = self.update_folder(folder_id=folder_id, list_ids=list_ids)
        return folder

    def get_note_id(self, task_id):
        """ Get the note_id for a specific task."""
        list_id = self.get_task(task_id)['list_id']
        for note in self.get_notes(list_id=list_id):
            if note['task_id'] == task_id:
                return note['id']
        raise KeyError('No note_id found for the given task_id.')
