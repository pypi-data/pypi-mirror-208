git_version_info
================

CFAB 2020

A very simple package for getting the git hash of the current repository and
adding it to a matplotlib plot. The two main commands are:

```
get_version()
```

...which returns the current git hash, and

```
tag_plot(small=True, ax=plt.gca())
```

...which adds the current hash to the given plot axis, optionally as a small tag
in the corner.
