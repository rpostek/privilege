1. w głownym katalogu projektu (piętro wyżej niż manage.py) wgrać plik web.config
2. <?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <httpPlatform processPath="C:\Users\rpostek\.virtualenvs\privilege-Q8xqppbZ\Scripts\python.exe" arguments="C:\Users\rpostek\PycharmProjects\privilege\sysusers\manage.py runserver %HTTP_PLATFORM_PORT%" stdoutLogEnabled="true" forwardWindowsAuthToken="true">
            <environmentVariables>
                <environmentVariable name="SERVER_PORT" value="%HTTP_PLATFORM_PORT%" />
            </environmentVariables>
        </httpPlatform>
        <handlers>
            <add name="MyPyHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
        </handlers>
        <security>
            <authentication>
                <anonymousAuthentication enabled="false" />
            </authentication>
        </security>
    </system.webServer>
</configuration>
3. zainstalować dodatek HttpPlatformHandler v1.2
https://www.iis.net/downloads/microsoft/httpplatformhandler
4. w IIS kliknąć na serwer i Certyfikaty serwera i 
5. Dodać witrynę i w ustawieniach aplikacji wpisać ścieżkę do katalogu głównego - z web.config
6. Dodać powiązanie https 443 * oraz wskazać certyfikat
7. Uwierzytelnianie - zablokować Uwierzytelnianie anonimowe
8. w edytorze konfiguracji system.webServer/httpPlatform forwardWindowsAuthToken -> True (chyba potrzebne)
9. jeśli serwer jest Windows 10/11 to dla adresów innych niż nazwa serwera trzeba zaimportować certyfikat oraz zezwolić na ten adres
w rejestrze Komputer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0 dodać zmienną BackConnectionHostNames typu REG_MULTI_SZ (multistring) i tam wpisać adres
bez tego nie działa Windows Authentication
Dodatkowo adres trzeba dodać w settings.py do HOST_ALLOWED.
https://stackoverflow.com/questions/7387156/unable-to-get-windows-authentication-to-work-through-local-iis 
