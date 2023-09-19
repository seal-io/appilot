from kubernetes import config, client


def get_service_endpoints(service):
    service_endpoints = []
    if service.spec.type == "NodePort":
        service_endpoints.extend(get_nodeport_service_endpoints(service))
    elif service.spec.type == "LoadBalancer":
        service_endpoints.extend(get_loadbalancer_service_endpoints(service))

    return service_endpoints


def get_loadbalancer_service_endpoints(service):
    if (
        service.status.load_balancer
        and "ingress" in service.status.load_balancer
    ):
        endpoints = []
        for ingress in service.status.load_balancer.ingress:
            if ingress.hostname != "":
                endpoints.append(
                    {
                        "name": service.name,
                        "endpoint": ingress.hostname,
                    }
                )
            elif ingress.ip != "":
                endpoints.append(
                    {
                        "name": service.name,
                        "endpoint": ingress.ip,
                    }
                )
        return endpoints
    else:
        return get_nodeport_service_endpoints(service)


def get_nodeport_service_endpoints(service):
    endpoints = []
    node_ip = get_node_ip()
    for port in service.spec.ports:
        endpoints.append(
            {
                "name": f"{service.metadata.name}/{port.name}",
                "endpoint": f"{node_ip}:{port.nodePort}",
            }
        )
    return endpoints


def get_ingress_endpoints(ingress):
    ingress_endpoints = []
    host = ""
    if ingress.status.load_balancer:
        for ing in ingress.status.load_balancer.ingress:
            if ing.hostname != "":
                host = ing.hostname
            else:
                host = ing.ip

    tlsHosts = []
    if ingress.spec.tls:
        for tls in ingress.spec.tls:
            tlsHosts.extend(tls.hosts)

    if ingress.spec.rules:
        for rule in ingress.spec.rules:
            scheme = "http"
            if rule.host in tlsHosts:
                scheme = "https"
            if rule.host != "":
                host = rule.host
            if host == "":
                continue
            if rule.http:
                for path in rule.http.paths:
                    if path.path != "":
                        ingress_endpoints.append(
                            {
                                "name": f"{ingress.name}/{path.path}",
                                "endpoint": f"{scheme}://{host}{path.path}",
                            }
                        )
                    else:
                        ingress_endpoints.append(
                            {
                                "name": f"{ingress.name}",
                                "endpoint": f"{scheme}://{host}",
                            }
                        )

    return ingress_endpoints


def get_node_ip() -> str:
    config.load_kube_config()
    core_v1 = client.CoreV1Api()
    nodes = core_v1.list_node()
    if nodes.items:
        node = nodes.items[0]
        for address in node.status.addresses:
            if address.type == "ExternalIP":
                return address.address
            elif address.type == "InternalIP":
                ip = address.address
        return ip

    raise Exception("No node found.")
