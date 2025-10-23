We are using free certbot for the ssl certification app will not work if the https fails 
`sudo certbot certificates` use this to see if the certificate is expired or not 
`sudo certbot certonly --nginx -d api.chat.studysend.com` use this to renew the certificate
use this to see if the ngnix is running 
sudo ss -tlnp | grep -E ':80|:443'

Use this to stop nginx 
sudo systemctl stop nginx

if nothing works to stop use 
sudo pkill -9 nginx

Start it cleanly 
sudo systemctl start nginx
sudo systemctl status nginx