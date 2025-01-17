This application pulls user and system allocation/usage data from the Texas Advanced Computing Center ([TACC](https://tacc.utexas.edu)) Allocation System ([TAS](https://tacc.utexas.edu/use-tacc/allocations/)) database. Data is retrieved in monthly .xlsl files. Then, using the [Pandas](https://pandas.pydata.org/docs/) and [Plotly Dash](https://dash.plotly.com/) external Python libraries, an [Nginx](https://www.nginx.com/) web server, and a TACC-partitioned VM, it creates a visual, interactive data dashboard with filters, charts, and graphs.

The application serves a dashboard that displays overall trends to all visitors, and shows sensitive user data only to visitors who are logged in.

The app is currently hosted [here](http://129.114.38.28).

Installation Instructions
------------
1. On your VM, pull the application files from the [GitHub repository](https://github.com/TACC/utrc-dashboard.git).

   ```
   git clone git@github.com:TACC/utrc-dashboard.git
   ```

2. In ./assets/data/monthly reports, add all monthly reports. Reports should follow the following naming convention: utrc_report_YYYY-MM-DD_to_YYYY-MM-DD.xlsx (e.g. utrc_report_2019-12-01_to_2020-01-01.xlsx).

3. In the root directory, add a .env file with the values `SECRET_KEY` and `ACCOUNTS`. `SECRET_KEY` should be a securely generated string. `ACCOUNTS` should contain a single json dictionary with usernames as keys and passwords as values. See `.env.sample` for an example.

4. Setup the Nginx web server configuration file to reverse proxy at port 8050.

   ```
   # /etc/nginx/sites-available/dashboard.conf
   server {
           listen 80;
           listen [::]:80;

           # Change to domain name
           server_name 129.114.38.28;

           location / {
                   proxy_pass http://localhost:8050;
           }
   }
   ```

5. Start the application.

   ```
   docker compose up --build -d
   ```

Updating Instructions
------------
1. Make changes inside the app directory.

2. While inside the main app directory, stop and restart the docker compose service.

   ```
   docker compose stop
   docker compose up --build -d
   ```