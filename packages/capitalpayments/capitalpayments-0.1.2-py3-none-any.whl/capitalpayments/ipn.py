from rest_framework.response import Response
from rest_framework.decorators import api_view

my_api_key = 'yout_api_key'
my_ipn_secret = 'yout_ipn_secret'

@api_view(['POST'])
def ipn(request):
    api_key = request.POST.get('api_key')
    ipn_secret = request.POST.get('ipn_secret')

    if api_key == my_api_key:
        if ipn_secret == my_ipn_secret:
            # @ todo
            print(request.POST)
            
            return Response({'status':200})
        else: 
            return Response({'Error': 'Invalid API key provided'})
    else:
        return Response({'Error': 'Invalid API key provided'})
