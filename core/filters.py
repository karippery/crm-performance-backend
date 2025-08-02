from django.db.models import Q
from datetime import datetime

def build_appuser_filters(params):
    """
    Builds Django Q objects for filtering AppUser based on provided parameters.
    
    Args:
        params (dict): Dictionary of filter parameters. Possible keys:
            - first_name: case-insensitive partial match
            - last_name: case-insensitive partial match
            - gender: exact match
            - customer_id: exact match
            - phone_number: case-insensitive partial match
            - birthday: exact date match
            - city: case-insensitive partial match on address.city
            - street: case-insensitive partial match on address.street
            - country: case-insensitive partial match on address.country
            - points_min: relationships.points greater than or equal
            - points_max: relationships.points less than or equal
            - last_activity_after: relationships.last_activity after this date
    
    Returns:
        Q: Django Q object combining all the provided filters
    """
    q = Q()

    if (fn := params.get("first_name")) and fn.strip():
        q &= Q(first_name__icontains=fn.strip())

    if (ln := params.get("last_name")) and ln.strip():
        q &= Q(last_name__icontains=ln.strip())

    if (gender := params.get("gender")) and gender.strip():
        q &= Q(gender=gender.strip())
        
    if (cid := params.get("customer_id")) and cid.strip():
        q &= Q(customer_id=cid.strip())
    
    if (phone := params.get("phone_number")) and phone.strip():
        q &= Q(phone_number__icontains=phone.strip())
    
    if bday := params.get("birthday"):
        try:
            if isinstance(bday, str):
                bday = datetime.strptime(bday, "%Y-%m-%d").date()
            q &= Q(birthday=bday)
        except (ValueError, TypeError):
            pass

    if (city := params.get("city")) and city.strip():
        q &= Q(address__city__icontains=city.strip())
    
    if (street := params.get("street")) and street.strip():
        q &= Q(address__street__icontains=street.strip())
    
    if (country := params.get("country")) and country.strip():
        q &= Q(address__country__icontains=country.strip())

    if pts_min := params.get("points_min"):
        try:
            q &= Q(relationships__points__gte=int(pts_min))
        except (ValueError, TypeError):
            pass
    
    if pts_max := params.get("points_max"):
        try:
            q &= Q(relationships__points__lte=int(pts_max))
        except (ValueError, TypeError):
            pass
    
    if last_activity := params.get("last_activity_after"):
        try:
            if isinstance(last_activity, str):
                last_activity = datetime.strptime(last_activity, "%Y-%m-%d")
            q &= Q(relationships__last_activity__gte=last_activity)
        except (ValueError, TypeError):
            pass

    return q