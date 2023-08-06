from thrivve_core import ThrivveCore


def get_prefix(service_url):
    app = ThrivveCore.get_app()
    final_url = ""
    service_name = app.config.get("SERVICE_NAME")
    if service_name:
        final_url += "/{}".format(service_name)

    final_url += service_url

    app.logger.debug(final_url)

    return final_url
