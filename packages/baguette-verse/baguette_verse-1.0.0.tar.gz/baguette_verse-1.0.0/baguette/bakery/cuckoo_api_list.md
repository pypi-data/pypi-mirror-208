## This is a list of all hooked Win32 APIs organized by category.

# __notification__
    __process__
    __anomaly__
    __exception__
    __missing__

# certificate
    CertControlStore
    CertCreateCertificateContext
    CertOpenStore
    CertOpenSystemStoreA
    CertOpenSystemStoreW

# crypto
    CryptAcquireContextA
    CryptAcquireContextW
    CryptCreateHash
    CryptDecrypt
    CryptEncrypt
    CryptExportKey
    CryptGenKey
    CryptHashData
    CryptDecodeMessage
    CryptDecodeObjectEx
    CryptDecryptMessage
    CryptEncryptMessage
    CryptHashMessage
    CryptProtectData
    CryptProtectMemory
    CryptUnprotectData
    CryptUnprotectMemory
    PRF
    Ssl3GenerateKeyMaterial

# exception
    SetUnhandledExceptionFilter
    RtlAddVectoredContinueHandler
    RtlAddVectoredExceptionHandler
    RtlDispatchException
    RtlRemoveVectoredContinueHandler
    RtlRemoveVectoredExceptionHandler

# file
    CopyFileA
    CopyFileExW
    CopyFileW
    CreateDirectoryExW
    CreateDirectoryW
    DeleteFileW
    DeviceIoControl
    FindFirstFileExA
    FindFirstFileExW
    GetFileAttributesExW
    GetFileAttributesW
    GetFileInformationByHandle
    GetFileInformationByHandleEx
    GetFileSize
    GetFileSizeEx
    GetFileType
    GetShortPathNameW
    GetSystemDirectoryA
    GetSystemDirectoryW
    GetSystemWindowsDirectoryA
    GetSystemWindowsDirectoryW
    GetTempPathW
    GetVolumeNameForVolumeMountPointW
    GetVolumePathNameW
    GetVolumePathNamesForVolumeNameW
    MoveFileWithProgressW
    RemoveDirectoryA
    RemoveDirectoryW
    SearchPathW
    SetEndOfFile
    SetFileAttributesW
    SetFileInformationByHandle
    SetFilePointer
    SetFilePointerEx
    NtCreateDirectoryObject
    NtCreateFile
    NtDeleteFile
    NtDeviceIoControlFile
    NtOpenDirectoryObject
    NtOpenFile
    NtQueryAttributesFile
    NtQueryDirectoryFile
    NtQueryFullAttributesFile
    NtQueryInformationFile
    NtReadFile
    NtSetInformationFile
    NtWriteFile

# iexplore
    COleScript_Compile
    CDocument_write
    CElement_put_innerHTML
    CHyperlink_SetUrlComponent
    CIFrameElement_CreateElement
    CScriptElement_put_src
    CWindow_AddTimeoutCode

# misc
    GetUserNameA
    GetUserNameW
    LookupAccountSidW
    GetComputerNameA
    GetComputerNameW
    GetDiskFreeSpaceExW
    GetDiskFreeSpaceW
    GetTimeZoneInformation
    WriteConsoleA
    WriteConsoleW
    CoInitializeSecurity
    UuidCreate
    GetUserNameExA
    GetUserNameExW
    ReadCabinetState
    SHGetFolderPathW
    SHGetSpecialFolderLocation
    EnumWindows
    GetCursorPos
    GetSystemMetrics

# netapi
    NetGetJoinInformation
    NetShareEnum
    NetUserGetInfo
    NetUserGetLocalGroups
    NetUserGetLocalGroups
    NetShareEnum

# network
    DnsQuery_A
    DnsQuery_UTF8
    DnsQuery_W
    GetAdaptersAddresses
    GetAdaptersInfo
    GetBestInterfaceEx
    GetInterfaceInfo
    ObtainUserAgentString
    URLDownloadToFileW
    DeleteUrlCacheEntryA
    DeleteUrlCacheEntryW
    HttpOpenRequestA
    HttpOpenRequestW
    HttpQueryInfoA
    HttpSendRequestA
    HttpSendRequestW
    InternetCloseHandle
    InternetConnectA
    InternetConnectW
    InternetCrackUrlA
    InternetCrackUrlW
    InternetGetConnectedState
    InternetGetConnectedStateExA
    InternetGetConnectedStateExW
    InternetOpenA
    InternetOpenUrlA
    InternetOpenUrlW
    InternetOpenW
    InternetQueryOptionA
    InternetReadFile
    InternetSetOptionA
    InternetSetStatusCallback
    InternetWriteFile
    ConnectEx
    GetAddrInfoW
    TransmitFile
    WSAAccept
    WSAConnect
    WSARecv
    WSARecvFrom
    WSASend
    WSASendTo
    WSASocketA
    WSASocketW
    WSAStartup
    accept
    bind
    closesocket
    connect
    getaddrinfo
    gethostbyname
    getsockname
    ioctlsocket
    listen
    recv
    recvfrom
    select
    send
    sendto
    setsockopt
    shutdown
    socket

# ole
    CoCreateInstance
    CoInitializeEx
    OleInitialize
    
# process
    CreateProcessInternalW
    CreateRemoteThread
    CreateThread
    CreateToolhelp32Snapshot
    Module32FirstW
    Module32NextW
    Process32FirstW
    Process32NextW
    ReadProcessMemory
    Thread32First
    Thread32Next
    WriteProcessMemory
    system
    NtAllocateVirtualMemory
    NtCreateProcess
    NtCreateProcessEx
    NtCreateSection
    NtCreateThread
    NtCreateThreadEx
    NtCreateUserProcess
    NtFreeVirtualMemory
    NtGetContextThread
    NtMakePermanentObject
    NtMakeTemporaryObject
    NtMapViewOfSection
    NtOpenProcess
    NtOpenSection
    NtOpenThread
    NtProtectVirtualMemory
    NtQueueApcThread
    NtReadVirtualMemory
    NtResumeThread
    NtSetContextThread
    NtSuspendThread
    NtTerminateProcess
    NtTerminateThread
    NtUnmapViewOfSection
    NtWriteVirtualMemory
    RtlCreateUserProcess
    RtlCreateUserThread
    ShellExecuteExW

# registry
    RegCloseKey
    RegCreateKeyExA
    RegCreateKeyExW
    RegDeleteKeyA
    RegDeleteKeyW
    RegDeleteValueA
    RegDeleteValueW
    RegEnumKeyExA
    RegEnumKeyExW
    RegEnumKeyW
    RegEnumValueA
    RegEnumValueW
    RegOpenKeyExA
    RegOpenKeyExW
    RegQueryInfoKeyA
    RegQueryInfoKeyW
    RegQueryValueExA
    RegQueryValueExW
    RegSetValueExA
    RegSetValueExW
    NtCreateKey
    NtDeleteKey
    NtDeleteValueKey
    NtEnumerateKey
    NtEnumerateValueKey
    NtLoadKey
    NtLoadKey2
    NtLoadKeyEx
    NtOpenKey
    NtOpenKeyEx
    NtQueryKey
    NtQueryMultipleValueKey
    NtQueryValueKey
    NtRenameKey
    NtReplaceKey
    NtSaveKey
    NtSaveKeyEx
    NtSetValueKey

# resource
    FindResourceA
    FindResourceExA
    FindResourceExW
    FindResourceW
    LoadResource
    SizeofResource
    
# services
    ControlService
    CreateServiceA
    CreateServiceW
    DeleteService
    EnumServicesStatusA
    EnumServicesStatusW
    OpenSCManagerA
    OpenSCManagerW
    OpenServiceA
    OpenServiceW
    StartServiceA
    StartServiceW

# synchronisation
    GetLocalTime
    GetSystemTime
    GetSystemTimeAsFileTime
    GetTickCount
    NtCreateMutant
    NtDelayExecution
    NtQuerySystemTime
    timeGetTime
    
# system
    LookupPrivilegeValueW
    GetNativeSystemInfo
    GetSystemInfo
    IsDebuggerPresent
    OutputDebugStringA
    SetErrorMode
    LdrGetDllHandle
    LdrGetProcedureAddress
    LdrLoadDll
    LdrUnloadDll
    NtClose
    NtDuplicateObject
    NtLoadDriver
    NtUnloadDriver
    RtlCompressBuffer
    RtlDecompressBuffer
    RtlDecompressFragment
    ExitWindowsEx
    GetAsyncKeyState
    GetKeyState
    GetKeyboardState
    SendNotifyMessageA
    SendNotifyMessageW
    SetWindowsHookExA
    SetWindowsHookExW
    UnhookWindowsHookEx
    
# ui
    DrawTextExA
    DrawTextExW
    FindWindowA
    FindWindowExA
    FindWindowExW
    FindWindowW
    GetForegroundWindow
    LoadStringA
    LoadStringW
    MessageBoxTimeoutA
    MessageBoxTimeoutW