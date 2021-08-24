import functools
import collections

import flask

BreadCrumb = collections.namedtuple('BreadCrumb', ['path', 'title'])

def breadcrumb(view_title):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Put title into flask.g so views have access and
            # don't need to repeat it
            flask.g.title = view_title
            # Also put previous breadcrumbs there, ready for view to use
            session_crumbs = flask.session.setdefault('crumbs', [])
            flask.g.breadcrumbs = []

            
            for path, title in session_crumbs:
                flask.g.breadcrumbs.append(BreadCrumb(path, title))

            flask.session.modified = True
            
            item = (flask.request.url, view_title)

            try:
                if item[1] not in [ i[1] for i in session_crumbs]:
                    session_crumbs.append(item)
                    
                else:
                    index = [ i[1] for i in session_crumbs].index(item[1])
                    length = len(session_crumbs)
                    for i in range (index+1 , length ):
                        session_crumbs.pop(i)
                    session_crumbs = session_crumbs[:index+1]
                    print('session_crumbs$$$$$$$$$$$$$$$$$$' , session_crumbs)
            except:
                pass


            

            # Call the view
            rv = f(*args, **kwargs)

            # Now add the request path and title for that view
            # to the list of crumbs we store in the session.
            # flask.session.modified = True
            # session_crumbs.append((flask.request.url, view_title))
            # item = (flask.request.url, view_title)
            # Only keep most recent crumbs (number should be configurable)
            if len(session_crumbs) > 5:
                session_crumbs.pop(0)
            
            
            return rv
        return decorated_function
    return decorator