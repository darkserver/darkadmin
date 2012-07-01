server {
        server_name %domain%;
        listen 80;
        root %home%/sites/%domain%;

        access_log /var/log/nginx/%user%/%domain%.access.log;
        error_log /var/log/nginx/%user%/%domain%.error.log;

#       if (!-e $request_filename) {
#               rewrite ^/(.+)$ /index.php?q=$1 last;
#       }

        location ~ \.php?$ {
                include templates/php;
                fastcgi_pass unix:/var/lib/darkadmin/php/%user%.sock;
        }

        location / {
                index index.php index.html;
                autoindex on;
        }
}

