# isa681project

Project for ISA681 course

## INITIAL SET UP:

1 - Enabling SSH: https://linuxize.com/post/how-to-enable-ssh-on-ubuntu-18-04/

2 - Setting up SSH keys: https://linuxize.com/post/how-to-set-up-ssh-keys-on-ubuntu-1804/

3 - Change the default SSH port (to 2255): https://linuxize.com/post/how-to-change-ssh-port-in-linux/

4 - Redirect port 2255 in the router

5 - Configure client SSH: https://linuxize.com/post/using-the-ssh-config-file/

6 - Create new user: isa681, pass: sacamosun10

7 - Remove the new user from the sudo list: sudo deluser cs681 sudo

8 - Create a subdomain (cs681project.twilightparadox.com) at https://freedns.afraid.org

9 - Configure ufw firewall: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04#step-3-%E2%80%94-allowing-ssh-connections

10 - Install Python: sudo apt install python3 python3-dev python3-pip python3-venv

11 - Install Flask: https://flask.palletsprojects.com/en/1.1.x/installation/#installation

12 - Create the Hello World: https://flask.palletsprojects.com/en/1.1.x/quickstart/#quickstart


## SSL/TLS:

1 - Install certbot and get certificates: https://certbot.eff.org/lets-encrypt/ubuntubionic-other

2 - Add CAA subdomains in freedns.afraid.org: https://ma.ttias.be/caa-checking-becomes-mandatory-ssltls-certificates/

3 - Follow these recommendations: https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices

4 - Get an A+ in: https://www.ssllabs.com/ssltest/analyze.html?viaform=on&d=isa681.twilightparadox.com%3A5000

4.1 - Disable TLS1.0 and TLS1.1: https://community.letsencrypt.org/t/disabling-tls-1-0-and-tls-1-1/112816

4.2 - Adding extra config: https://ssl-config.mozilla.org/#server=apache&version=2.4.41&config=modern&openssl=1.1.1&guideline=5.4



## APACHE:

1 - Install and configure mod_wsgi: https://modwsgi.readthedocs.io/en/master/user-guides/quick-installation-guide.html

https://modwsgi.readthedocs.io/en/master/user-guides/quick-configuration-guide.html

2 - Create the .wsgi file: https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/

3 - Install and set up Apache: https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-18-04#step-5-%E2%80%94-setting-up-virtual-hosts-(recommended)

4 - SSL in Apache: https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html

5 - Redirect every conection to https: https://www.namecheap.com/support/knowledgebase/article.aspx/9821/38/apache-redirect-to-https



## GIT:

1- Docs: https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository

2 - GitHub's .gitignore file examples: https://github.com/github/gitignore

3 - Cheatseet: https://github.com/trein/dev-best-practices/wiki/Git-Tips



## FLASK:

1 - Tutorial: https://flask.palletsprojects.com/en/1.1.x/tutorial/

2 - Youtube videos: https://www.youtube.com/playlist?list=PLLjmbh6XPGK4ISY747FUHXEl9lBxre4mM

3 - Flask Cheatsheet: https://s3.us-east-2.amazonaws.com/prettyprinted/flask_cheatsheet.pdf

4 - SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

5 - Flask-WTF: https://flask-wtf.readthedocs.io/en/stable/index.html

6 - Flask-Login: https://flask-login.readthedocs.io/en/latest/

7 - Flask-Bcrypt: https://flask-bcrypt.readthedocs.io/en/latest/

8 - Flask-Nav: https://pythonhosted.org/flask-nav/index.html

9 - Flask-Bootstrap: https://pythonhosted.org/Flask-Bootstrap/basic-usage.html

10 - Flask-SocketiIO: https://flask-socketio.readthedocs.io/en/latest/



## Extras:

1 - Recaptcha: https://john.soban.ski/add-recaptcha-to-your-flask-application.html

2 - Videos chat app: https://www.youtube.com/watch?v=RdSrkkrj3l4
