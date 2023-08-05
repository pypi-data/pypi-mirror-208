def available_companies(request):
    
    context_data = { 'available_companies': []}
    
    if request.user.is_authenticated:
        context_data['available_companies'] = request.user.available_companies.all()

    return context_data