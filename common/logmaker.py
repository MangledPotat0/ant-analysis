import git
import os


def log_generator(expids):

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    hash_info = 'git_hash: {}'.format(sha)
    fnames = 'exp_ids: {}'.format(expids)
    print(hash_info)
    print(fnames)






# EOF
