# This is a sample Python script.
import subprocess
import json
from module import pullRequestData, commitData, projectData
import mysql.connector


#
# 　git clone
#
def gitClone():
    repository_url = 'https://github.com/NAIST-SE/DevGPT.git'
    destination_directory = '/Users/watanabemiku/PycharmProjects/MsrChallenge/DevGPT'

    try:
        subprocess.check_call(['git', 'clone', repository_url, destination_directory])
        print(f'Repository cloned to {destination_directory}')
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')


#
# 　Extract data from snapshot
#
def readJson(filePath):
    Request_Data = {}
    AllProject_list = set()
    FilteredProject_list = set()
    AllPR = set()
    AllLink =set()
    FilteredPR = set()
    Id = 0

    with open(filePath) as f:
        di = json.load(f)

    for source in di['Sources']:
        author = source.get('Author', [])
        create_time = source.get('CreatedAt', [])
        body = source.get('Body', [])[:1000]
        AllProject_list.add(str(source.get('RepoName', [])))
        AllPR.add(source.get('URL', []))
        chatgpt_sharing = source.get('ChatgptSharing', [])

        for chatgpt in chatgpt_sharing:
            mentions = chatgpt.get('Mention', [])
            mentioned_url = mentions.get('MentionedURL', [])
            AllLink.add(mentioned_url)
            mentioned_author = mentions.get('MentionedAuthor', [])
            mentioned_text = mentions.get('MentionedText', [])[:1000]

            if author != mentioned_author:
                FilteredProject_list.add(str(source.get('RepoName', [])))
                FilteredPR.add(source.get('URL', []))

                Id += 1
                Request_Data[Id] = pullRequestData.PullRequstData(author, body, mentioned_author, mentioned_text,
                                                                  mentioned_url,
                                                                  create_time)

    allCommitData = projectData.projectData(len(AllProject_list), len(FilteredProject_list), len(AllPR),
                                            len(FilteredPR), len(AllLink), len(Request_Data))
    pullResult = commitData.commitData(allCommitData, Request_Data)
    return pullResult


#
# create DB
#
def creatTable(cursor):
    cursor.execute("DROP TABLE IF EXISTS pr_commit_list")
    try:
        cursor.execute("""CREATE TABLE pr_commit_list(
                       id INT(11) AUTO_INCREMENT NOT NULL,
                       directory VARCHAR(1000) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       author VARCHAR(100) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       createtime VARCHAR(100) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       reviewer varchar(100) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       body VARCHAR(5000) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       mention VARCHAR(5000) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       url VARCHAR(1000) NOT NULL COLLATE utf8mb4_unicode_ci , 
                       PRIMARY KEY (id)
                       )""")
    except Exception as e:
        print(f"Error creating table: {e}")


#
# Add data
#
def addDataBase(cursor, directory, author, reviewer, body, mention, url, create_time):
    # Add data
    sql = "INSERT INTO pr_commit_list(directory, author, createtime,reviewer, body, mention, url) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, (directory, author, create_time,reviewer, body, mention, url))
    connection.commit()


#
# delete same commit
#
def deleteSamecommit(json_dict):
    validator = set()
    distinct_PRs = []
    for _, pre_value in json_dict.items():
        for _, p_value in pre_value.Request_Data.items():
            if p_value.get_string() in validator:
                # print("already exist")
                pass
            else:
                distinct_PRs.append(p_value)
                validator.add(p_value.get_string())
    return distinct_PRs


if __name__ == '__main__':

    connection = mysql.connector.connect(
        host='db',
        user='user',
        passwd='password',
        db='pr_commit_db')
    cursor = connection.cursor()

    creatTable(cursor)

    fileHead = "../DevGPT/"
    filePath = [  # "snapshot_20230727/20230727_195927_pr_sharings.json",
        # "snapshot_20230803/20230803_093947_pr_sharings.json",
        # "snapshot_20230810/20230810_123110_pr_sharings.json",
        # "snapshot_20230817/20230817_125147_pr_sharings.json",
        # "snapshot_20230824/20230824_100450_pr_sharings.json",
        # "snapshot_20230831/20230831_060603_pr_sharings.json",
        # "snapshot_20230907/20230907_091631_pr_sharings.json",
        # "snapshot_20230914/20230914_074826_pr_sharings.json",
        "snapshot_20231012/20231012_233628_pr_sharings.json"]

    json_dict = {}
    for path in filePath:
        json_dict[path] = readJson(fileHead + path)

    for k, data in json_dict.items():
        print(data.allCommitData.get_string())
        for value in data.Request_Data.values():
            if k == "snapshot_20231012/20231012_233628_pr_sharings.json":
                addDataBase(cursor, k, value.writeAuthor, value.reviewAuthor, value.body, value.mention, value.url,
                            value.create_time)

    PRs = deleteSamecommit(json_dict)
