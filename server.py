import asyncio

HOST = 'localhost' 
PORT = 9095         

connected_clients = set()  
stop_server = False        

async def handle_echo(reader, writer):
    """
    Асинхронная функция для обработки подключений от клиентов.
    """
    global connected_clients
    addr = writer.get_extra_info('peername') 
    print(f"Клиент подключился: {addr}")
    connected_clients.add(writer)  
    try:
        while True:
            data = await reader.read(100)  
            if not data:
                
                print(f"Клиент отключился: {addr}")
                break
            message = data.decode()  
            print(f"Получено {message!r} от {addr}")

            
            writer.write(data)
            await writer.drain()  

            print(f"Отправлено: {message!r} обратно к {addr}")

    except ConnectionResetError:
        
        print(f"Клиент принудительно отключился: {addr}")
    finally:
        
        connected_clients.discard(writer)
        writer.close()  
        await writer.wait_closed()  
        print(f"Соединение закрыто с {addr}")

async def stop_server_when_no_clients(server):
    """
    Асинхронная функция для остановки сервера, когда получена команда 'stop' и нет подключенных клиентов.
    """
    global stop_server
    while True:
        await asyncio.sleep(1) 
        if stop_server and not connected_clients:
            
            print("Нет подключенных клиентов, сервер останавливается...")
            server.close()  
            await server.wait_closed()  
            break

async def read_server_commands(loop):
    """
    Асинхронная функция для чтения команд с серверной консоли.
    """
    global stop_server
    while True:
        
        cmd = await loop.run_in_executor(None, input)
        if cmd.strip() == 'stop':
            print("Команда 'stop' получена. Остановка сервера после отключения клиентов.")
            stop_server = True  
            break

async def main():
    """
    Основная асинхронная функция для настройки и запуска сервера.
    """
    server = await asyncio.start_server(handle_echo, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Сервер запущен на {addrs}')

    loop = asyncio.get_running_loop()

    server_task = loop.create_task(server.serve_forever())
    command_task = loop.create_task(read_server_commands(loop))
    stop_task = loop.create_task(stop_server_when_no_clients(server))

    tasks = [server_task, command_task, stop_task]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("Сервер прерван пользователем (Ctrl+C)")
        server.close()
        await server.wait_closed()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        print("Сервер остановлен")

if __name__ == '__main__':
    asyncio.run(main())
