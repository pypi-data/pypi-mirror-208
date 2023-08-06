# -*- coding: utf-8 -*-

from datetime import datetime
from sunpeek.common.unit_uncertainty import Q
from pint import Quantity
from sunpeek.components.types import CollectorType
from sunpeek.components.iam_methods import IAM_Method


class CollectorTypeSST:
    def __new__(cls, eta0hem: Q, a1: Q, a2: Q, ceff: Q, test_reference_area: Q, gross_length: Q,
                iam_method: IAM_Method, kd=None,
                name: str = None, manufacturer_name: str = None, product_name: str = None, licence_number: str = None,
                area_gr: Q = None, area_ap: Q = None, gross_width: Q = None, gross_height: Q = None,
                description: str = None, certificate_date_issued: datetime = None, certificate_lab: str = None,
                certificate_details: str = None, test_report_id: str = None, f_prime: Q = None
                ):
        test_type = "SST"
        a5 = ceff
        return CollectorType(
            test_reference_area=test_reference_area, test_type=test_type, gross_length=gross_length, name=name,
            manufacturer_name=manufacturer_name, product_name=product_name,
            test_report_id=test_report_id, licence_number=licence_number,
            certificate_date_issued=certificate_date_issued, certificate_lab=certificate_lab,
            certificate_details=certificate_details, area_gr=area_gr, area_ap=area_ap, gross_width=gross_width,
            gross_height=gross_height, a1=a1, a2=a2, a5=a5, kd=kd, eta0hem=eta0hem, iam_method=iam_method, f_prime=f_prime)


class CollectorTypeQDT:
    def __new__(cls, eta0b: Quantity, a1: Quantity, a2: Q, a5: Q, kd: Q, test_reference_area: str, gross_length: Q,
                iam_method: IAM_Method,
                name: str = None, manufacturer_name: str = None, product_name: str = None, licence_number: str = None,
                area_gr: Q = None, area_ap: Q = None, gross_width: Q = None, gross_height: Q = None,
                description: str = None, certificate_date_issued: datetime = None, certificate_lab: str = None,
                certificate_details: str = None, test_report_id: str = None, f_prime: Q = None
                ):
        test_type = "QDT"
        return CollectorType(
            test_reference_area=test_reference_area, test_type=test_type, gross_length=gross_length, name=name,
            manufacturer_name=manufacturer_name, product_name=product_name,
            test_report_id=test_report_id, licence_number=licence_number, certificate_date_issued=certificate_date_issued,
            certificate_lab=certificate_lab, certificate_details=certificate_details,
            area_gr=area_gr, area_ap=area_ap, gross_width=gross_width, gross_height=gross_height,
            a1=a1, a2=a2, a5=a5, kd=kd, eta0b=eta0b,
            iam_method=iam_method, f_prime=f_prime)
