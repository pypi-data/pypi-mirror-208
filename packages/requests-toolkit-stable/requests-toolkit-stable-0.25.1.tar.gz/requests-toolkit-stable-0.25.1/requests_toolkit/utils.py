def  in_jupyter_notebook():
    # 定义一个变量，表示是否在 ipython 会话中
    _in_ipython_session = False
    try:
        # 尝试获取 __IPYTHON__ 这个变量
        __IPYTHON__
        # 如果没有异常，说明在 ipython 会话中
        _in_ipython_session = True
    except NameError:
        # 如果出现异常，说明不在 ipython 会话中
        _in_ipython_session = False

    # 打印结果
    return _in_ipython_session