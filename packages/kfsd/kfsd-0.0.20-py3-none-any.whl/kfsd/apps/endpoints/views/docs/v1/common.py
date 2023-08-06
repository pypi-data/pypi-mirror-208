from drf_spectacular.utils import OpenApiExample


class CommonV1Doc:
    @staticmethod
    def config_examples():
        return [
            OpenApiExample(
                'CONFIG',
                media_type='application/json',
                value={
                    "output": {
                        "value": {
                            "templates": [
                                {
                                    "template": "istio/networking.istio.io/v1alpha3/gateway.json",
                                    "dimensions": [],
                                    "globalvars": {
                                        "__TEMPLATE_ID__": "gateway"
                                    }
                                }
                            ],
                            "overrides": {
                                "gateway": {
                                    "spec": {
                                        "servers": [
                                            {
                                                "port": "{{ values.gateway.virtualhost0.listen }}",
                                                "hosts": "{{ values.gateway.virtualhost0.hosts }}"
                                            }
                                        ]
                                    }
                                }
                            },
                            "values": {
                                "gateway": {
                                    "metadata": {
                                        "name": "istio-gateway",
                                        "namespace": "istio-system"
                                    },
                                    "virtualhost0": {
                                        "listen": {
                                            "number": 80,
                                            "name": "http-snappyguide",
                                            "protocol": "HTTP"
                                        },
                                        "hosts": [
                                            "dev.snappyguide.com",
                                            "dev.accounts.snappyguide.com"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    "op": "CONFIG"
                },
                request_only=False,
                response_only=False
            ),
            OpenApiExample(
                'CONFIG',
                media_type='application/json',
                value={
                    "op": "CONFIG",
                    "input": {
                        "dimensions": {"environment": "k8s", "cluster": "mac", "type": "dev"},
                        "raw_config": [
                            {
                                "setting": [
                                    "master"
                                ],
                                "templates": [
                                    {
                                        "template": "istio/networking.istio.io/v1alpha3/gateway.json",
                                        "dimensions": [],
                                        "globalvars": {
                                            "__TEMPLATE_ID__": "gateway"
                                        }
                                    }
                                ],
                                "overrides": {
                                    "gateway": {
                                        "spec": {
                                            "servers": [
                                                {
                                                    "port": "{{ values.gateway.virtualhost0.listen }}",
                                                    "hosts": "{{ values.gateway.virtualhost0.hosts }}"
                                                }
                                            ]
                                        }
                                    }
                                },
                                "values": {
                                    "gateway": {
                                        "metadata": {
                                            "name": "istio-gateway",
                                            "namespace": "istio-system"
                                        },
                                        "virtualhost0": {
                                            "listen": {
                                                "number": 80,
                                                "name": "http-snappyguide",
                                                "protocol": "HTTP"
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "setting": [
                                    "environment:k8s",
                                    "cluster:mac",
                                    "type:dev"
                                ],
                                "values": {
                                    "gateway": {
                                        "virtualhost0": {
                                            "hosts": [
                                                "dev.snappyguide.com",
                                                "dev.accounts.snappyguide.com"
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                "setting": [
                                    "environment:k8s",
                                    "cluster:inhouse",
                                    "type:prod"
                                ],
                                "values": {
                                    "gateway": {
                                        "virtualhost0": {
                                            "hosts": [
                                                "snappyguide.com",
                                                "accounts.snappyguide.com"
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                request_only=True,
                response_only=False
            ),
        ]
