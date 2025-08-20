def data_tables(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active:
        if request.user.is_superuser or request.user.is_staff:
            crews = CrewMember.objects
        else:
            crews = CrewMember.objects.filter(user=request.user)

        search = request.POST.get('search[value]', None)
        if search is not None:
            crews = crews.filter(
                Q(first_name__contains=search) |
                Q(last_name__contains=search) |
                Q(role__contains=search) |
                Q(expertise_level__contains=search)
            )

        role_search = request.POST.get('columns[3][search][value]', '').replace('\\', '')
        if len(role_search) > 0:
            crews = crews.filter(role=role_search)

        level_search = request.POST.get('columns[4][search][value]', '').replace('\\', '')
        if len(level_search) > 0:
            crews = crews.filter(expertise_level=level_search)

        order = request.POST.get('order[0][column]', '0')
        order_type = request.POST.get('order[0][dir]', 'asc')
        order_mapping = {
            '0': 'id',
            '1': 'first_name',
            '2': 'last_name',
            '3': 'role',
            '4': 'expertise_level',
            '5': 'is_active'
        }
        if order_type == 'asc':
            crews = crews.order_by(f'-{order_mapping[order]}')
        else:
            crews = crews.order_by(f'{order_mapping[order]}')

        page_size = int(request.POST.get('length', 10))
        page_start = int(request.POST.get('start', 0))
        data = {
            "draw": int(request.POST.get('draw', 1)),
            "recordsTotal": crews.count(),
            "recordsFiltered": crews.count(),
            "data": []
        }
        crews = crews.all()[page_start:page_start + page_size]

        for crew in crews:
            data['data'].append({
                'id': crew.id,
                'first_name': crew.first_name,
                'last_name': crew.last_name,
                'role': crew.role,
                'expertise_level': crew.expertise_level,
                'is_active': 'Active' if crew.is_active else 'Inactive',
                'action': f'<button class="btn btn-primary btn-sm" onclick="edit_crew({crew.id})">Edit</button>'
            })
        return JsonResponse(data, content_type='application/json', status=200)
    else:
        return JsonResponse({'message': "Method is invalid."}, content_type='application/json', status=400) 