# Simple 8 Channel Relay Plugin for Indigo

This plugin is using the HTTP protocol to access and direct an 8 Channel Relay board RELAY-NET-V5.8 from IotZone. It was built as a spinoff downsize of David Newhall's plugin effort (see [here](https://github.com/davidnewhall/indigo-8channel-relay)). 

All sprinkler related code has been removed. A subprocess is used with `curl` to transmit commands to the board through HTTP (normally on port 80). As the documentation for the board is lacking for the other supported protocols (port 1234 and Modbus port 502), this was the only found way to make it works (Many trials have been done with Modbus and older port 1234 protocols but nothing worked).

You can install the indigo plugin, downloading the zip file from the releases page [here](https://github.com/turgu1/indigo-simple-8channel-relay/releases).

## License

- [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.


<img src="picture/relay-net-v5.8.jpg" alt="picture" width="800"/>
