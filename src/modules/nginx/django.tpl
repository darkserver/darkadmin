server {
	server_name %domain%;
	listen 80;
	root /home/%user%/sites/%domain%;

	access_log /var/log/nginx/%user%/%domain%/.access.log;
	error_log /var/log/nginx/%user%/%domain%/.error.log;

# redirect server error pages to the static page /50x.html
	error_page   500 502 503 504  /50x.html;

	location /admin/static {
		alias %home%/sites/%domain%/admin/media;
		expires 1w;
	}

	location /static {
		alias %home%/sites/%domain%/static;
		expires 1w;
	}

	location / {
		fastcgi_pass unix:/var/lib/darkadmin/django/%user%/%domain%.sock;
		include templates/fastcgi_django;
	}
}

