import os,sys
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(parent_directory)
import string
import random
sys.path.append(parent_directory)
from intern_project.models import Report
from .fetch_report import generate_report
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED,HTTP_404_NOT_FOUND, HTTP_200_OK

def generate_random_string():
    return random.randrange(1,1000000000)


@api_view(['GET'])
def trigger_report(request):
    # report_id = int()
    report = Report.objects.create(status="Running",report_id=generate_random_string())

    generate_report.delay(report.id)

    return Response({"report_id": report.id}, status=HTTP_202_ACCEPTED)






@api_view(['GET'])
def get_report(request,report_id):
    try:
        print(report_id)
        report_id = request.query_params.get('report_id')
        report = Report.objects.get(report_id=report_id)
        csv_file_path='reports'

        if report.status == "Running":
            return Response({'status':'Running'})
    
        elif report.status =="Complete" and report.csv_file:
            with open(csv_file_path, 'rb') as csv_file:
                    response = HttpResponse(csv_file.read(), content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="report_{report_id}.csv"'
                    return response
    except Report.DoesNotExist:
        pass
    
    return Response({'status':'Report Not Found'},status=404)