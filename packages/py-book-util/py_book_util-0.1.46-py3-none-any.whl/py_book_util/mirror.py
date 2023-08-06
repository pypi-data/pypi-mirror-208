def add_config_option(config, section_name, option_name, option_val):
    if config.has_section(section_name) == False:
        config.add_section(section_name)
    config.set(section_name, option_name, option_val)


def save_config_in_order(config, filename):
    import configparser

    new_config = configparser.ConfigParser()
    sections = config.sections()
    sections.sort()
    for section_name in sections:
        options = config.options(section_name)
        options.sort()
        for option_name in options:
            option_val = config.get(section_name, option_name)
            print("%s %s %s", section_name, option_name, option_val)
            add_config_option(new_config, section_name, option_name, option_val)
    new_config.write(open(filename, "w"))


def enable_rust_cargo_mirror():
    import os

    # for k, v in os.environ.items():
    #   print(f'{k}={v}')
    assert os.environ["USERPROFILE"]
    rust_cargo_config_file = os.environ["USERPROFILE"] + "/.cargo/config"
    if os.path.isfile(rust_cargo_config_file) == False:
        with open(rust_cargo_config_file, "w") as file:
            file.write("")
    import configparser

    config = configparser.ConfigParser()
    config.read(rust_cargo_config_file, encoding="utf-8")

    section_name = "source.crates-io"
    option_name = "registry"
    option_val = '"https://github.com/rust-lang/crates.io-index"'
    add_config_option(config, section_name, option_name, option_val)
    option_name = "replace-with"
    option_val = '"tuna"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "source.my-crates-io"
    option_name = "registry"
    option_val = '"https://ghproxy.com/https://github.com/rust-lang/crates.io-index"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "source.ustc"
    option_name = "registry"
    option_val = '"https://mirrors.ustc.edu.cn/crates.io-index"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "source.sjtu"
    option_name = "registry"
    option_val = '"https://mirrors.sjtug.sjtu.edu.cn/git/crates.io-index/"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "source.tuna"
    option_name = "registry"
    option_val = '"https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "source.rustcc"
    option_name = "registry"
    option_val = '"https://code.aliyun.com/rustcc/crates.io-index.git"'
    add_config_option(config, section_name, option_name, option_val)

    section_name = "http"
    option_name = "check-revoke"
    option_val = "false"
    add_config_option(config, section_name, option_name, option_val)

    section_name = "net"
    option_name = "git-fetch-with-cli"
    option_val = "true"
    add_config_option(config, section_name, option_name, option_val)

    # config.write(open(rust_cargo_config_file, 'w'))
    save_config_in_order(config, rust_cargo_config_file)
    return rust_cargo_config_file
