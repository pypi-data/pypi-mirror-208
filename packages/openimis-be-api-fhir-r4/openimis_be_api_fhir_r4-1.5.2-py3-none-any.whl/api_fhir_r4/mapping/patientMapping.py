from insuree.models import Profession, Education, IdentificationType, Relation, Gender

from api_fhir_r4.configurations import GeneralConfiguration


class RelationshipMapping(object):
    relationship = {
        str(relation.id): relation.relation for relation in Relation.objects.all()
    }


class EducationLevelMapping(object):
    education_level = {
        str(education.id): education.education for education in Education.objects.all()
    }


class PatientProfessionMapping(object):
    patient_profession = {
        str(profession.id): profession.profession for profession in Profession.objects.all()
    }


class IdentificationTypeMapping(object):
    identification_type = {
        identification.code: identification.identification_type for identification in IdentificationType.objects.all()
    }


class MaritalStatusMapping(object):
    marital_status = {
        "M": "Married",
        "S": "Single",
        "D": "Divorced",
        "W": "Widowed",
        "UNK": "unknown"
    }


class PatientCategoryMapping(object):
    GENDER_SYSTEM = "http://hl7.org/fhir/administrative-gender"
    AGE_SYSTEM = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/usage-context-age-type"

    fhir_patient_category_coding = {
        "male": {
            "system": GENDER_SYSTEM,
            "code": "male",
            "display": "Male",
        },
        "female": {
            "system": GENDER_SYSTEM,
            "code": "female",
            "display": "Female",
        },
        "adult": {
            "system": AGE_SYSTEM,
            "code": "adult",
            "display": "Adult",
        },
        "child": {
            "system": AGE_SYSTEM,
            "code": "child",
            "display": "Child",
        },
    }

    def get_genders():
        imis_gender_mapping = {
            # FHIR Gender code to IMIS object
            'male': Gender.objects.get(pk='M'),
            'female': Gender.objects.get(pk='F'),
        }

        o = Gender.objects.filter(pk='O').first()
        if o:
            imis_gender_mapping['other'] = o
        return imis_gender_mapping

    imis_gender_mapping = get_genders()

    imis_patient_category_flags = {
        "male": 1,
        "female": 2,
        "adult": 4,
        "child": 8,
    }
