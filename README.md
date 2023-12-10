# On the Use of ChatGPT for Code Review


## Content
 In this repository, the code extracts the data required by PR from MSRchallenge snapshots.　
## Source code
 Our main source code is located in 'MsrChallenge/msrchallenge' directory.

### Require
・Docker(> 20.10.13)


### Database
| Attribute   | Description                                             |
|-------------|---------------------------------------------------------|
| directory   | Snapshot name                                           |
| Author      | Author who introduced this mention                      |
| create_time | When the author created this pull request               |
| Reviewr     | Who mentioned this shared ChatGPT link                  |
| Body        | Description of this pull request                        |
| Mention     | The context when this shared ChatGPT link was mentioned |
| URL         | URL to the mentioned source                             |

### Run
This program is designed to run on docker.<br>
You can run the python file by executing the following command
```
docker-compose build
docker-compose up
```
 