import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ThemeToggle } from './theme-toggle';
import type { SessionData } from '../types/analysis';

interface FileUploadProps {
  onSessionCreated: (sessionData: SessionData) => void;
}

export function FileUpload({ onSessionCreated }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:3003/api/create-session', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const sessionData = await response.json();
      onSessionCreated(sessionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4 relative landing-background">
      {/* Animated background particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl animate-bounce-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-bounce-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Theme toggle positioned in top-right corner */}
      <div className="absolute top-4 right-4 animate-fade-in z-10">
        <ThemeToggle />
      </div>
      
      <Card className="w-full max-w-md hero-card hover-lift relative z-10">
        <CardHeader className="text-center space-y-4">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-glow-pulse"></div>
              <div className="relative bg-primary/10 p-4 rounded-full">
                <svg 
                  className="w-16 h-16 text-primary" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" 
                  />
                </svg>
              </div>
            </div>
          </div>
          <CardTitle className="text-3xl font-bold hero-title text-primary">
            OS-Pulse Analysis Platform
          </CardTitle>
          <CardDescription className="hero-subtitle text-base">
            Upload a file to start real-time Windows API monitoring and behavioral analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 animate-fade-in" style={{ animationDelay: '0.6s', opacity: 0 }}>
          <div className="space-y-3">
            <div className="relative group">
              <Input
                type="file"
                onChange={handleFileChange}
                accept="*/*"
                className="cursor-pointer transition-all duration-300 hover:border-primary/50 hover:shadow-md"
              />
              {file && (
                <div className="mt-3 p-3 bg-primary/5 border border-primary/20 rounded-lg animate-slide-in-up">
                  <div className="text-sm text-muted-foreground flex items-start gap-2">
                    <svg className="w-4 h-4 text-primary animate-bounce-slow flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate" title={file.name}>{file.name}</p>
                      <p className="text-xs text-muted-foreground/70">({(file.size / 1024).toFixed(1)} KB)</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-500 bg-red-50 dark:bg-red-950 p-4 rounded-lg border border-red-200 dark:border-red-900 animate-shake flex items-start gap-2">
              <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <Button 
            onClick={handleUpload} 
            disabled={!file || isUploading}
            className="w-full button-ripple relative overflow-hidden group transition-all duration-300 hover-lift"
          >
            {isUploading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="spinner w-4 h-4 border-2"></span>
                <span>Uploading...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
                <span>Start Analysis</span>
              </span>
            )}
          </Button>

          {/* Feature highlights */}
          <div className="grid grid-cols-3 gap-3 pt-4 border-t border-border feature-grid">
            <div className="text-center p-2 rounded-lg bg-muted/50 hover-scale cursor-default">
              <div className="text-2xl mb-1">⚡</div>
              <div className="text-xs text-muted-foreground">Real-time</div>
            </div>
            <div className="text-center p-2 rounded-lg bg-muted/50 hover-scale cursor-default">
              <div className="text-2xl mb-1">🔒</div>
              <div className="text-xs text-muted-foreground">Secure</div>
            </div>
            <div className="text-center p-2 rounded-lg bg-muted/50 hover-scale cursor-default">
              <div className="text-2xl mb-1">📊</div>
              <div className="text-xs text-muted-foreground">Detailed</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}