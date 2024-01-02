
# Run the code

You can find my code for the first assignment in this private repository:
https://github.com/fabioakr/tp3_cloud_computing.

In order to run the project you should follow the following steps:

1. Clone the GitHub project repository to your computer.
2. If you haven’t already, please create a free-tier personal account on AWS. This
is important for you to be able to successfully use IAM and SSM services, as
aforementioned.
3. Log into your AWS account selecting the “Root user”, which allows you to access
the IAM and SSM services directly, without any other constraints that might be in
effect by default on the “IAM user”. 
4. On the upper right corner, click on your username and then, click on “Security
credentials”. After that, please create an access key on that page. You should
save the .cvs file, because the secret access key is not retrievable from the web
console after its creation. Note that it doesn’t generate the session token, as in
the Educational version of AWS that we used for the two previous TPs, because
this access key is not temporary.
5. Go to the file “/.aws/credentials” and paste both the access key ID and secret
access key.
6. To automatically deploy the standalone MySQL benchmark, run the
“run_standalone_mysql.py” file. Bear in mind that it will take a considerable time
to fire up the instance with MySQL and the benchmarking app, but should
present the benchmark results on the terminal, before concluding and
terminating the instance.
7. To automatically deploy the cluster MySQL benchmark, run the
“run_cluster_mysql.py” file. Bear in mind that it will also take a considerable time
to fire up the whole cluster, because it now involves the setup of four instances.
