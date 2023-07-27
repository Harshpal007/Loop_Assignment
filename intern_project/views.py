import os,sys
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(parent_directory)
sys.path.append(parent_directory)
from get_report import generate_report
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED,HTTP_404_NOT_FOUND, HTTP_200_OK

@api_view(['POST'])
def trigger_report(request):
    report_id = generate_report.delay()

    return Response({"report_id": report_id}, status=HTTP_202_ACCEPTED)






@api_view(['GET'])
def get_report(request):
    report_id = request.query_params.get('report_id', None)
    if not report_id:
        return Response({"error": "report_id parameter is required."}, status=HTTP_404_NOT_FOUND)

    # Check the status of the Celery task
    task = generate_report.AsyncResult(report_id)
    if task.state == 'SUCCESS':
        # Report generation is complete, and CSV data is ready.
        csv_data = "store_id, uptime_last_hour, uptime_last_day, update_last_week, downtime_last_hour, downtime_last_day, downtime_last_week\n"
        # Add the CSV data rows here...

        # Return the report status and CSV data in the response
        response_data = {
            "report_id": report_id,
            "status": "Complete",
            "csv_data": csv_data,
        }
        return Response(response_data, status=HTTP_200_OK)
    elif task.state == 'PENDING':
        # Report generation is still running.
        return Response({"status": "Running"}, status=HTTP_202_ACCEPTED)
    else:
        # Report generation has failed or some other state.
        return Response({"status": "Error"}, status=HTTP_200_OK)