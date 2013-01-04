// $Id$

#ifndef QUICKYPIX_CGI_SU_H
#define QUICKYPIX_CGI_SU_H

/*
 * HTTPD_USER -- Define as the username under which Apache normally
 *               runs.  This is the only user allowed to execute
 *               this program.
 */
#ifndef HTTPD_USER
#define HTTPD_USER "www-data"
#endif

/*
 * SAFE_PATH -- Define a safe PATH environment to pass to CGI executables.
 *
 */
#ifndef AP_SAFE_PATH
#define AP_SAFE_PATH "/usr/local/bin:/usr/bin:/bin"
#endif

#ifndef QUICKYPIX_UNAME
#error "Need to define QUICKYPIX_UNAME"
#endif

#ifndef QUICKYPIX_GNAME
#error "Need to define QUICKYPIX_GNAME"
#endif

#ifndef QUICKYPIX_CMD
#error "Need to define QUICKYPIX_CMD"
#endif

#endif
