#  coding: utf-8 
import SocketServer
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    
    data = ""
    root = "/www"
    acceptableExtensions = (".html", ".css", "/")
    requestResult = ""
    requestContent = ""
    requestOutput = -1
    resource = ""
    
    def handle(self):
        # Set the default returned results
        self.set_default_results()
        
        # Base code, but I also split the data into a list for ease of parsing. Split is done on white spaces.
        self.data = self.request.recv(1024).strip()
        
        # Make sure there is actually data.
        if (self.data == None or self.data == ""):
            return
        
        #print ("Got a request of: %s" % self.data)
        self.data = self.data.split() # Separate lines because I don't want to chain method calls on one line since it becomes hard to read
        
        # Assume that the input always follows the same format
        if (self.verify_request(self.data[0]) == False):
            self.return_results()
            return
        
        self.process_request(self.data[1])  
        
        # Send request results
        self.return_results()
        
        # Check if the resource request is OK
        if (self.requestOutput == 200):
            self.serve_resource()
        return
    
    # Processes the request
    def process_request(self, filePath):
        # Checking end of string for acceptable file extensions. If the extension is not recognized, return HTML error.
        # Ref: http://stackoverflow.com/questions/18351951/check-if-string-ends-with-one-of-the-strings-from-a-list
        # Author: falsetru
        # Retrieved: Jan 19, 2017
        if (filePath.endswith(self.acceptableExtensions) == False):
            self.set_404_result()
            return

        # Check if the file path exists.
        if (os.path.exists(os.curdir + self.root + filePath) == False):
            self.set_404_result()
            return        
        
        # Check if request is for directory
        if (filePath[-1] == '/'):
            self.retrieve_index(filePath)
            return
        
        # Get the resources
        self.retrieve_resource(filePath)
        
        # Return the request as a .html mime type
        if (filePath.endswith(".html")):
            self.requestContent = "Content-Type: text/html\r\n\r\n"
            return
        
        # Return the result as a .css mime type
        self.requestContent = "Content-Type: text/css\r\n\r\n"
        return

# Resource retrieval 
# Requests that are servable have their resources retrieved for serving here
    def retrieve_index(self, directory):
        self.resource = os.curdir + self.root + directory + "index.html"
        return
    
    def retrieve_resource(self, file):
        self.resource = os.curdir + self.root + file
        return

# Request result setters
# The results of the requests are changed/set according to server requirements

    # Verify that the REST request is GET only
    # Returns False if the REST request is not GET; else return True
    def verify_request(self, request):
        if (request != "GET"):
            self.requestResult = "HTTP/1.1 405 Method Not Allowed\r\n"
            self.requestOutput = 405
            return False
        return True    
    
    # The default returned results.
    # Ref: The mime typing idea was inspired by http://stackoverflow.com/questions/7282187/python-urllib-post-with-different-content-type-than-urlencoded
    # Author: Steven
    # Retrieved: Jan 19, 2017
    def set_default_results(self):
        self.requestResult = "HTTP/1.1 200 OK\r\n"
        self.requestContent = "Content-Type: text/html\r\n\r\n" #Since we return index.html upon folder request, the default mime type is HTML
        self.requestOutput = 200
        return
    
    def set_404_result(self):
        self.requestResult = "HTTP/1.1 404 Not FOUND!\r\n"
        self.requestOutput = 404       
        return

# Request responses and resource service

    # Send request results to all clients
    def return_results(self):
        self.request.sendall(self.requestResult)
        self.request.sendall(self.requestContent)
        return
    
    # Serve a resource
    def serve_resource(self):
        file = open(self.resource, "r")
        self.request.sendall(file.read())
        file.close()
        return
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
