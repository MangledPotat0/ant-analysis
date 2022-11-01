import git
import os


# TODO: Work in progress; need to check that this actually works

# Whenever the log generator is called, it will create a dictionary that
# contains all the information needed to reproduce the output. Currently this
# amounts to the list of source files used, and the git hash for the code that
# was used (basically, to keep track of the code version information). Another
# field should be added later to save the parameters.

def log_generator(expids):

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    hash_info = 'git_hash: {}'.format(sha)
    fnames = 'exp_ids: {}'.format(expids)
    print(hash_info)
    print(fnames)

    logdict = {'hash': sha, 'exp_ids': expids}

    return logdict





# EOF
