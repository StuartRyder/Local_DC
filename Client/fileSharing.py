from ast import Try
import json
import os
import socket
import sys
from threading import Thread, current_thread, Event, Lock

import tqdm
from colors import bcolors

from .utils import encodeJSON, getFile, recvall


class FileSharingFunctionalities:
    def __init__(self):
        self.port2 = None  # File sharing port
        self.filelock = Lock()
        self.displayFiles = {}
        self.hostedFiles = {}
        self.FileTakingclients = []
        self.isOnline = True

    def receiveFile(self,client,conn,pause1,file: tuple):
        fileID, start, end, filesize, filepath,completed_bytes = file
        print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Downloading path:= {bcolors["UNDERLINE"]}{filepath}{bcolors["ENDC"]}')
        progress = tqdm.tqdm(range(filesize), f'{bcolors["OKGREEN"]}Downloading{bcolors["ENDC"]}', unit="B", unit_scale=True, unit_divisor=1024,)
        if fileID in client.fileTaking.keys():
            client.fileTaking[fileID][3] = pause1
        else:
            client.fileTaking[fileID] = [start,0,False,pause1,filepath]
        with open(filepath, 'wb') as output:
            output.seek(4096 * start)
            progress.update(completed_bytes)
            while start < end:
                try:
                    data = recvall(conn, min(4096, filesize - completed_bytes))
                    if not data:
                        print(f'{bcolors["FAIL"]}[CLIENT]_receiveFile error! {bcolors["ENDC"]}')
                        print(f'{bcolors["HEADER"]}Reason:{bcolors["ENDC"]} Client went offline!')
                        break
                    output.write(data)
                    completed_bytes += len(data)
                    progress.update(len(data))
                    start += 1
                    if(pause1.is_set()):
                        pause1.clear()
                        with self.filelock:
                            client.fileTaking[fileID] = [start, completed_bytes, True, pause1,filepath]
                        pause1.wait()
                        pause1.clear()
                        client.fileTaking[fileID][2] = False
                except Exception as error:
                    print(f'{bcolors["FAIL"]}[CLIENT]Failed to listen to {bcolors["ENDC"]}')
                    print(f'{bcolors["HEADER"]}Reason:{bcolors["ENDC"]} {error}')
                    break
                
            if client.fileTaking[fileID][1] == filesize:
                with self.filelock:
                    del(client.fileTaking[fileID])
                print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Download completed 😊\n>>', end='')
            # closing the connection
            conn.close()
            sys.exit()

            # debug
            # print(f'\n{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Chunks received:{start}/{end}')
            # print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Closed connection with the peer.')

    def _clientInteraction(self, conn, pause1):
        while True:
            try:
                command = input('>>>')
                if(command == 'p'):
                    pause1.set()
                    res = {"type": "pause_request"}
                elif(command == 'r'):
                    pause1.set()
                    res = {"type": "play_request"}
                conn.sendall(encodeJSON(res))
            except:
                sys.exit()

    def _listenClientForRequests(self, client: tuple):
        conn, addr = client
        pause2 = Event()
        while True:
            try:
                # Note:file receiveing client closes the connection
                client_request = str(conn.recv(4096), 'utf-8')
                if len(client_request) == 0:
                    print(f'{bcolors["FAIL"]}[CLIENT]{addr} went offline!{bcolors["ENDC"]}')
                    self._closeFileClient(client)
                client_request = json.loads(client_request)

                # debug client_request
                # print(client_request)

                if client_request['type'] == 'pause_request':
                    # print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Pause request...')
                    pause2.set()
                elif client_request['type'] == 'play_request':
                    # print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Play request...')
                    pause2.set()
                elif client_request['type'] == 'download_request':
                    data = client_request['data']
                    if data["fileID"] not in self.hostedFiles.keys():
                        res = {"type": "response", "data": None,
                               "error": "No such file exist,closing the connection."}
                        conn.sendall(encodeJSON(res))
                        self._closeFileClient(client)
                    res = {"type": "response", "data": "OK", "error": None}
                    conn.sendall(encodeJSON(res))
                    t = Thread(target=self._sendClientFile, args=(
                        pause2, client, data), name=f'_sendClientFile{client[0]}')
                    t.start()
                else:
                    res = {"type": "response", "data": None,
                           "error": "Invalid request,closing the connection"}
                    conn.sendall(encodeJSON(res))
            except socket.error as error:
                # print(f'{bcolors["FAIL"]}[CLIENT]Failed to listen to {addr}{bcolors["ENDC"]}')
                # print(f'{bcolors["HEADER"]}Reason:{bcolors["ENDC"]} {error}')
                self._closeFileClient(client)

    def _sendClientFile(self, pause2, client: tuple, data: dict):
        conn, addr = client

        start = data["start"]
        end = data["end"]

        filename, filePath,fileSize,  = self.hostedFiles[data["fileID"]]

        with open(filePath, 'rb') as output:
            output.seek(4096 * start)
            while start < end:
                try:
                    byteData = output.read(4096)
                    if not byteData:
                        break
                    conn.sendall(byteData)
                    start += 1
                    if(pause2.is_set()):
                        pause2.clear()
                        if self.isOnline == False:
                            sys.exit()
                        pause2.wait()
                        pause2.clear()

                except Exception as error:
                    print(
                        f'{bcolors["FAIL"]}[CLIENT]Error sending file to client := {addr}{bcolors["ENDC"]}')
                    print(
                        f'{bcolors["HEADER"]}Reason:{bcolors["ENDC"]} {error}')
                    break

        sys.exit()

        # debug
        # print(f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Chunks sent:{start}/{end}.Closing connection...')

    def _closeFileClient(self, client: tuple):
        conn, addr = client
        conn.close()
        sys.exit()

    def _closeFileSocket(self):
        print(
            f'{bcolors["WARNING"]}[CLIENT]{bcolors["ENDC"]}Closing file socket...')
        self.file_socket.close()
        sys.exit()
