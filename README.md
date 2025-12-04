<img src="" align="center" height="50%" width="50%">

# **GFinder (GUI Finder)**

**GFinder** is a powerful, locally-hosted web utility to perform deep system enumeration, regex pattern matching, and artifact hunting across your local file system.

Unlike standard command-line tools like grep or find, GFinder offers an interactive GUI with context visualization, making it easier to spot hardcoded secrets, analyze code flow, and audit file structures.

## **🚀 Features**

### **Core Functionality**

* **Web-Based GUI:** Runs entirely in your terminal but controlled via a sleek, responsive web interface in your browser.  
* **Dual Search Engines:** Toggle between **Literal String** matching and full **Regular Expressions (Regex)**.  
* **Context Awareness:** View matches in their original context with adjustable lines of code before and after the hit (essential for code auditing).

### **Advanced Scoping**

* **Multi-Target Search:** Search within **File Content**, **File Names**, **Directory Names**, or **All** simultaneously.  
* **Exact Match Mode:** eliminate false positives by enforcing strict start/end matching (e.g., finding key won't return keyboard).  
* **Deep Filtering:**  
  * **File Type:** Filter by Text, Binary, or Executables.  
  * **Extensions:** Whitelist specific extensions (e.g., py, js, conf, pem).  
  * **Root Path:** Set any directory as the starting point (e.g., /var/www, C:\\Users\\Admin).

## **📋 Prerequisites**

* **Python 3+**  
* **Flask** (Python Web Framework)

## **🛠️ Installation**

1. Clone or Download the Script  
   Save the tool script as gfinder.py.  
2. Install Dependencies  
   GFinder only requires Flask to run the web server.  
   pip install flask

## **💻 Usage**

1. Start the Tool  
   Run the script from your terminal:
   ```
   python3 gfinder.py
   ```

3. Access the Interface  
   Open your web browser and navigate to:  
```
   http://127.0.0.1:5000/
```
5. Stop the Tool  
   Press CTRL+C in your terminal to shut down the server.

## **🔍 Interface Guide**

### **The Toolbar**

| Control | Description |
| :---- | :---- |
| **Search Bar** | Enter your keyword, variable name, or regex pattern here. |
| **Root Path** | The starting directory for the scan (Default: .). Use absolute paths for best results. |
| **Find In (Target)** | Select scope: File Content, File Names, Dir Names, or All. |
| **File Type** | Filter matches by Text, Binary, or Executable files. |
| **Extensions** | Comma-separated list of extensions to scan (e.g., py,env,yaml). |

### **The Toggles**

* **Regex Mode:** Interprets the search term as a Python Regular Expression.  
* **Exact Match:** Forces the search to match the entire string/line exactly.  
* **Case Sensitive:** Respects capitalization (e.g., "Error" will not match "error").  
* **Context Lines:** Number of lines to display before and after a content match.

## **⚡ Examples**

**1\. Finding Hardcoded AWS Keys (Pentesting)**

* **Search Term:** AKIA\[0-9A-Z\]{16}  
* **Regex Mode:** ON  
* **Target:** File Content  
* **Extensions:** py, js, txt, env, json

**2\. Locating a Specific Executable**

* **Search Term:** nmap  
* **Target:** File Names  
* **File Type:** Executables Only

**3\. Auditing a Project for "TODO" Comments**

* **Search Term:** TODO  
* **Target:** File Content  
* **Context Lines:** 3 (To see what task is pending)

## **⚠️ Security Warning**

GFinder runs with the permissions of the user who executes the Python script.

* **Do not** host this on a public IP address.  
* **Do not** run this script as root or Administrator unless absolutely necessary, as it exposes your entire file system to the web interface (even if local).

## **📄 License**

Open Source. Feel free to modify and distribute.
