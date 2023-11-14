
# Run the code

You can find our code for the first assignment is in this private repository:
https://github.com/houskkam/advanced_cloud_computing.


In order to run the project you should follow the following steps:
1. Clone the GitHub project repository.
2. Start AWS Academy Session.
3. Make sure that Docker is running
4. With AWS Academy session running, click on AWS Details → AWS CLI → Show
button.
5. Make sure to be inside the advanced_cloud_computing directory
6. Copy the information of the AWS Academy session to the .env file following this
mappings:
- AWS_ACCESS_KEY_ID: aws_access_key_id
- AWS_SECRET_ACCESS_KEY: aws_secret_access_key
- AWS_SESSION_TOKEN: aws_session_token
7. Run the following commands inside project directory
- chmod +x scripts.sh
- ./scripts.sh

When you run the scripts.sh bash script it will create the Docker that will install all
dependencies and run all the process. The process include creating many objects in
your environment. It creates a key pair, then it creates a security group, then it creates
a virtual private cloud (VPC), a load balancer, two target groups, nine instances and
finally, one listener and the forward rules. It also runs the benchmarking scripts and it
saves the graphs in the results directory.