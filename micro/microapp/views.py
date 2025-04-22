from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .relay_control import RelayController
import serial.tools.list_ports

# Create your views here.
def home(request):
    return render(request, 'microapp/home.html')

def register(request):
    return render(request, 'microapp/register.html')

def film(request):
    return render(request, 'microapp/film.html')

def list_com_ports():
    """List available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def control(request):
    relays = range(1, 9)  # Create a range of relay numbers
    com_ports = list_com_ports()  # Get available COM ports
    return render(request, 'microapp/control.html', {'relays': relays, 'com_ports': com_ports})

def handoff(request):
    return render(request, 'microapp/handoff.html')

def explore(request):
    return render(request, 'microapp/explore.html')

def report(request):
    return render(request, 'microapp/report.html')

def settings(request):
    return render(request, 'microapp/settings.html')

def login(request):
    return render(request, 'microapp/login.html')

def language(request):
    return render(request, 'microapp/language.html')

@csrf_exempt
def control_relay(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        com_port = request.POST.get('com_port', 'COM13')  # Default to COM7

        print(f"Received request to perform action: {action} on {com_port}")

        try:
            controller = RelayController(com_port)
            if action == 'light':
                controller.set_light_mode()
            elif action == 'dark':
                controller.set_dark_mode()
            elif action == 'machine_on':
                controller.machine_on()
            elif action == 'machine_off':
                controller.machine_off()
            elif action in ['on', 'off']:
                relay_number = request.POST.get('relay')
                if action == 'on':
                    controller.relay_on(relay_number)
                else:
                    controller.relay_off(relay_number)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})

            controller.close()
            return JsonResponse({'status': 'success', 'message': f"{action} executed successfully"})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
