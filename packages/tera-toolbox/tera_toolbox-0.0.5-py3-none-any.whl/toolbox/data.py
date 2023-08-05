from supabase import create_client

url = "https://sygrjcqvvnsrvxczpnpx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5Z3JqY3F2dm5zcnZ4Y3pwbnB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzU3MDgxMDUsImV4cCI6MTk5MTI4NDEwNX0.dK4303KKaNo4pE5ATtJdA0qukSVTsnMxAzWZjU30SW0"


def holidays(calendar):
    supabase = create_client(url, key)
    response = supabase.table('feriados').select(
        'data, descricao').eq('calendario', calendar).execute()
    return response.data
