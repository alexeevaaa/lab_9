import asyncio

HOST = 'localhost'
PORT = 9095

async def tcp_echo_client(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    message = 'Hello, world'
    
    
    writer.write(message.encode())
    await writer.drain()
    
    
    data = await reader.read(100)
    writer.close()
   

loop = asyncio.get_event_loop()
task = loop.create_task(tcp_echo_client(HOST, PORT))
loop.run_until_complete(task)
HOST = 'localhost'  
PORT = 9095         


async def tcp_echo_client():
    """
    Асинхронная функция для подключения к серверу и обмена сообщениями.
    """
    reader = None
    writer = None
    loop = asyncio.get_running_loop()
    try:
        while True:
            try:
                reader, writer = await asyncio.open_connection(HOST, PORT)
                print(f"Подключено к серверу {HOST}:{PORT}")
                break 
                
            except ConnectionRefusedError:
                
                print(f"Не удалось подключиться к серверу {HOST}:{PORT}. Повтор через 5 секунд...")
                await asyncio.sleep(5)
        
        while True:
            
            message = await loop.run_in_executor(None, input, "Введите сообщение (или 'exit' для выхода): ")
            if message.lower() == 'exit':
                
                print("Отключение от сервера.")
                break
           
            writer.write(message.encode())
            await writer.drain()  # Ждем, пока данные будут отправлены
            
            data = await reader.read(100)
            if not data:
                
                print("Сервер закрыл соединение.")
                break
            print(f"Получено эхо: {data.decode()!r}")
    except KeyboardInterrupt:
       
        print("\nКлиент прерван пользователем (Ctrl+C)")
    except ConnectionResetError:
        
        print("Соединение было закрыто сервером.")
    finally:
        if writer is not None:
            writer.close()  
            await writer.wait_closed()
        print("Клиент завершил работу.")
if __name__ == '__main__':
    
    asyncio.run(tcp_echo_client())
