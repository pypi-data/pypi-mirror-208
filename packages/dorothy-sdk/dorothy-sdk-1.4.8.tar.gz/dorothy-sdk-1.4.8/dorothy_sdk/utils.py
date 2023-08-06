def url_join(*args):
    url_args = []
    for element in args:
        if not isinstance(element, str):
            raise RuntimeError("Only elements of type 'str' are accepted.")
        else:
            if element.endswith("/"):
                element = element[:-1]
            if element.startswith("/"):
                element = element[1:]
            url_args.append(element)
    return "/".join(url_args)

