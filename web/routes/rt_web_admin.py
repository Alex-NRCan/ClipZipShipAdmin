"""
This module, implementing OpenAPI concepts, manages the various routes for the web interface.

End points:
 - /admin : endpoint to a page to Admin page
 - /admin/users : endpoint to a page to Manage users
"""

# Application imports
from core import config, user
from . import routes
import core.routes.rt_core as rt_core


@routes.route('/admin')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_ADMIN)
def html_admin_index():
    """
    Handles a GET request on "/" end point to load an HTML page for the Admin Home page.
    """

    try:
        return rt_core.render_page('admin/home.html')

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('home.html')


@routes.route('/admin/users')
@rt_core.validate_user_html_level(config.ROLE_LEVEL_ADMIN)
def html_admin_users():
    """
    Handles a GET request on "/" end point to load an HTML page for the Admin Users page.
    """

    try:
        return rt_core.render_page('admin/users.html', users=user.get_users())

    except Exception as err:
        # Weird, just proceed
        print(err)
        return rt_core.render_page('home.html')
