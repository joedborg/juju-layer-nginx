from charmhelpers.core.templating import render
from charmhelpers.core import hookenv
import toml
import sys
from shell import shell


def load_site():
    try:
        with open('site.toml') as fp:
            conf = toml.loads(fp.read())
        return conf
    except IOError:
        hookenv.status_set('blocked',
                           'No site.toml found, not configuring vhost')
        sys.exit(0)


def configure_site(site, template, **kwargs):
    """ configures vhost

    Arguments:
    site: Site name
    template: template to process in templates/<template.conf>
    context: dict() sites.toml
    **kwargs: additional dict items to append to template variables
    """
    hookenv.status_set('maintenance', 'Configuring site {}'.format(site))

    config = hookenv.config()
    context = load_site()
    context['host'] = config['host']
    context['port'] = config['port']
    render(source=template,
           target='/etc/nginx/sites-enabled/{}'.format(site),
           context=context)
    hookenv.log('Wrote vhost config {} to {}'.format(context, template),
                'info')

    if 'packages' in context:
        install_extra_packages(context['packages'])


def install_extra_packages(pkgs):
    """ Installs additional packages defined
    """
    hookenv.status_set('maintenance',
                       'Installing additional packages {}'.format(pkgs))
    if isinstance(pkgs, str):
        pkgs = [pkgs]

    sh = shell('apt-get install -qy {}'.format(" ".join(pkgs)))
    if sh.code > 0:
        hookenv.status_set(
            'blocked',
            'Unable to install packages: {}'.format(sh.errors()))
        sys.exit(0)
