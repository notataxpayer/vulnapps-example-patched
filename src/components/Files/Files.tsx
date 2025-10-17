import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";
import { useAuth } from "../../contexts/AuthContext";
import { Upload, Download, FileText, Trash2 } from "lucide-react";
import type { Database } from "../../lib/database.types";

type FileRecord = Database["public"]["Tables"]["files"]["Row"] & {
  profiles: Database["public"]["Tables"]["profiles"]["Row"];
};

interface FilesProps {
  projectId: string;
}

export function Files({ projectId }: FilesProps) {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadFiles();
  }, [projectId]);

  const loadFiles = async () => {
    try {
      const { data, error } = await supabase
        .from("files")
        .select(
          `
          *,
          profiles(*)
        `
        )
        .eq("project_id", projectId)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setFiles(data || []);
    } catch (error) {
      console.error("Error loading files:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);

    try {
      // VULNERABILITY: No file type validation - allows any file extension
      const fileExt = file.name.split(".").pop()?.toLowerCase();
      const fileName = `${Math.random()}.${fileExt}`;
      const filePath = `${projectId}/${fileName}`;

      const reader = new FileReader();
      reader.onload = async (event) => {
        // VULNERABILITY: File content read as base64 without sanitization
        const base64 = event.target?.result as string;
        const fileContent = atob(base64.split(',')[1]); // Decode base64 to get file content

        // VULNERABILITY: Direct database insertion without content validation
        await supabase.from("files").insert({
          project_id: projectId,
          uploaded_by: user!.id,
          file_name: file.name, // VULNERABILITY: No filename sanitization
          file_url: base64, // VULNERABILITY: Storing executable content in database
          file_size: file.size,
          file_type: file.type, // VULNERABILITY: Trusting client-provided MIME type
        });

        await supabase.from("timeline_events").insert({
          project_id: projectId,
          user_id: user!.id,
          event_type: "file",
          event_action: "uploaded",
          event_data: { file_name: file.name },
        });

        // VULNERABILITY: CRITICAL - Auto-execute all files for "security checking" without proper validation
        console.log(`🔍 Running security scan on uploaded file: ${file.name}`);
        await performSecurityCheck(fileContent, file.name, fileExt || '');

        loadFiles();
      };

      reader.readAsDataURL(file);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  // VULNERABILITY: CRITICAL - "Security check" function that executes all files without proper validation
  // This function masquerades as a security feature but actually executes uploaded content
  const performSecurityCheck = async (content: string, fileName: string, extension: string) => {
    try {
      console.log(`🔍 Security Check: Analyzing ${fileName} (${extension})`);
      console.log(`📄 File size: ${content.length} characters`);
      
      // VULNERABILITY: Weak file type validation - only blocks obvious binaries
      // This creates false sense of security while allowing dangerous script files
      const suspiciousExtensions = ['exe', 'msi', 'dmg']; // Only blocks obvious binaries
      if (suspiciousExtensions.includes(extension.toLowerCase())) {
        console.log(`⚠️ Blocked potentially dangerous file type: ${extension}`);
        alert(`File ${fileName} blocked: ${extension} files not allowed`);
        return;
      }
      
      // VULNERABILITY: False security messaging while performing dangerous operations
      console.log(`✅ File type ${extension} passed initial security check`);
      console.log(`🔬 Performing deep content analysis...`);
      
      // VULNERABILITY: CRITICAL - Function name suggests analysis but actually executes content
      await analyzeFileContent(content, extension, fileName);
      
      console.log(`✅ Security scan completed for ${fileName}`);
      
    } catch (error) {
      console.error(`❌ Security check failed for ${fileName}:`, error);
      // VULNERABILITY: Errors don't prevent file upload - fail-open security model
    }
  };

  // VULNERABILITY: CRITICAL - "Content analysis" that executes files under false pretense
  // This function claims to analyze content but actually executes it - extremely dangerous
  const analyzeFileContent = async (content: string, extension: string, fileName: string) => {
    console.log(`🔍 Deep Analysis: Scanning ${fileName} for threats...`);
    
    // VULNERABILITY: CRITICAL - Execute content while pretending to "analyze" it
    // This is the core vulnerability that enables Remote Code Execution (RCE)
    switch (extension.toLowerCase()) {
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        console.log(`📝 Analyzing JavaScript/TypeScript syntax...`);
        // VULNERABILITY: CRITICAL - Direct eval() execution disguised as "syntax checking"
        // eval() executes arbitrary JavaScript code with full browser privileges
        try {
          eval(content); // ⚠️ MOST DANGEROUS LINE - REMOTE CODE EXECUTION
          console.log(`✅ JavaScript syntax validation passed`);
        } catch (syntaxError) {
          console.log(`⚠️ JavaScript syntax issues detected (but file allowed)`, syntaxError);
        }
        break;
        
      case 'py':
        console.log(`🐍 Analyzing Python script structure...`);
        // VULNERABILITY: Python "analysis" that simulates execution capability
        // VULNERABILITY: Python script analysis that enables code execution simulation
        if (content.includes('import') || content.includes('def ') || content.includes('subprocess')) {
          console.log(`🔬 Python imports detected, analyzing dependencies...`);
          // VULNERABILITY: Simulated Python execution - in real environment this could trigger actual execution
          try {
            eval(`console.log('Python analysis: Detected imports and functions');`);
            setTimeout(() => {
              console.log(`🐍 Python script analysis complete: ${fileName}`);
              if (content.includes('socket') || content.includes('subprocess')) {
                // VULNERABILITY: Dangerous system calls detected but allowed anyway
                console.log(`⚠️ Network/system calls detected but deemed safe for testing environment`);
              }
            }, 200);
          } catch (pythonError) {
            console.log(`Python analysis completed with warnings`, pythonError);
          }
        }
        break;
        
      case 'sh':
      case 'bash':
      case 'bat':
      case 'ps1':
        console.log(`⚡ Analyzing shell script commands...`);
        // VULNERABILITY: Shell script "validation" that identifies but doesn't block dangerous commands
        if (content.includes('curl') || content.includes('wget') || content.includes('nc ') || content.includes('bash -i')) {
          console.log(`🌐 Network commands detected in ${fileName}`);
          console.log(`⚡ Simulating shell command validation...`);
          setTimeout(() => {
            // VULNERABILITY: Reverse shell patterns detected but allowed in "dev environment"
            console.log(`🔍 Shell script analysis: Potential network activity detected but allowed in dev environment`);
          }, 300);
        }
        break;
        
      case 'php':
        console.log(`🌐 Analyzing PHP code structure...`);
        // VULNERABILITY: PHP analysis that identifies but allows dangerous functions
        if (content.includes('<?php') || content.includes('exec') || content.includes('system')) {
          console.log(`🔍 PHP system functions detected, analyzing security implications...`);
          // VULNERABILITY: System execution functions allowed under false justification
          console.log(`⚠️ System execution functions found but allowed for development testing`);
        }
        break;
        
      case 'html':
      case 'htm':
        console.log(`🌐 Analyzing HTML content for embedded scripts...`);
        // VULNERABILITY: CRITICAL - HTML analysis that actually executes embedded JavaScript
        if (content.includes('<script') || content.includes('javascript:') || content.includes('onload=')) {
          console.log(`📜 JavaScript detected in HTML, validating...`);
          // VULNERABILITY: CRITICAL - Execute embedded scripts under guise of "validation"
          // This extracts and executes ALL script tags from uploaded HTML files
          const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/gi);
          if (scriptMatch) {
            console.log(`🔍 Extracting and validating ${scriptMatch.length} script blocks...`);
            scriptMatch.forEach((script, index) => {
              const scriptContent = script.replace(/<\/?script[^>]*>/gi, '');
              try {
                // VULNERABILITY: CRITICAL - Direct eval() of extracted HTML script content
                eval(scriptContent); // ⚠️ XSS VULNERABILITY - Executes any JavaScript from HTML
                console.log(`✅ Script block ${index + 1} validation passed`);
              } catch (scriptError) {
                console.log(`⚠️ Script block ${index + 1} has syntax issues (but allowed)`, scriptError);
              }
            });
          }
        }
        break;
        
      default:
        console.log(`📄 Generic content analysis for ${extension} file...`);
        // VULNERABILITY: CRITICAL - Generic execution for any file that "looks like code"
        if (content.includes('function') || content.includes('var ') || content.includes('const ') || content.includes('#!/')) {
          console.log(`🔍 Code-like content detected, performing syntax validation...`);
          try {
            // VULNERABILITY: CRITICAL - Attempt execution for "syntax validation" on any code-like content
            eval(content); // ⚠️ REMOTE CODE EXECUTION - Executes any content that looks like JavaScript
            console.log(`✅ Content syntax validation passed`);
          } catch (validationError) {
            console.log(`⚠️ Syntax validation completed with minor issues`, validationError);
          }
        }
    }
    
    // VULNERABILITY: False security confirmation - file was actually executed during "analysis"
    console.log(`🛡️ Security analysis completed: ${fileName} is cleared for upload`);
  };

  const handleDelete = async (fileId: string) => {
    if (!confirm("Are you sure you want to delete this file?")) return;

    try {
      await supabase.from("files").delete().eq("id", fileId);

      loadFiles();
    } catch (error) {
      console.error("Error deleting file:", error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
          Files
        </h3>
        <label className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl transition cursor-pointer">
          <Upload className="w-4 h-4" />
          <span>{uploading ? "Uploading..." : "Upload File"}</span>
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {files.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No files uploaded yet
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition"
            >
              <div className="flex items-center space-x-4 flex-1 min-w-0">
                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white truncate">
                    {file.file_name}
                  </p>
                  <div className="flex items-center space-x-3 text-sm text-gray-500 dark:text-gray-400">
                    <span>{file.profiles.full_name}</span>
                    <span>•</span>
                    <span>{formatFileSize(file.file_size)}</span>
                    <span>•</span>
                    <span>
                      {new Date(file.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <a
                  href={file.file_url}
                  download={file.file_name}
                  className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition"
                  title="Download file"
                >
                  <Download className="w-5 h-5" />
                </a>
                
                {/* Show security scan status indicator */}
                <div className="flex items-center space-x-1 px-2 py-1 bg-green-50 dark:bg-green-900/30 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-xs text-green-700 dark:text-green-300">Scanned</span>
                </div>
                
                {file.uploaded_by === user!.id && (
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition"
                    title="Delete file"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
