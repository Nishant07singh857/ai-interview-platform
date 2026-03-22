'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useResume } from '@/hooks/useResume'
import { FileUploader } from '@/components/resume/FileUploader'
import { ResumeAnalysis } from '@/components/resume/ResumeAnalysis'
import { GapAnalysis } from '@/components/resume/GapAnalysis'
import { LearningRoadmap } from '@/components/resume/LearningRoadmap'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs/Tabs'
import { Card, CardContent } from '@/components/ui/card/Card'
import { Button } from '@/components/ui/button/Button'
import { motion } from 'framer-motion'

export default function ResumePage() {
  const router = useRouter()
  const { user } = useAuth()
  const {
    currentResume,
    parsedResume,
    analysis,
    gapAnalysis,
    roadmap,
    isLoading,
    uploadResume,
    parseResume,
    analyzeResume,
    analyzeGaps,
    generateRoadmap,
  } = useResume()

  const [selectedCompany, setSelectedCompany] = useState<string>('')
  const [selectedRole, setSelectedRole] = useState<string>('')

  const handleUpload = async (file: File) => {
    const resume = await uploadResume(file)
    if (resume) {
      await parseResume(resume.resumeId)
      await analyzeResume(resume.resumeId)
    }
  }

  const handleGapAnalysis = async () => {
    if (currentResume && selectedCompany && selectedRole) {
      await analyzeGaps(currentResume.resumeId, selectedCompany, selectedRole)
    }
  }

  const handleGenerateRoadmap = async () => {
    if (currentResume && selectedCompany && selectedRole) {
      await generateRoadmap(currentResume.resumeId, selectedCompany, selectedRole)
    }
  }

  const companies = [
    { name: 'Google', roles: ['ML Engineer', 'Data Scientist', 'Software Engineer'] },
    { name: 'Amazon', roles: ['Applied Scientist', 'Data Scientist', 'ML Engineer'] },
    { name: 'Microsoft', roles: ['Data Scientist', 'ML Engineer', 'Research Scientist'] },
    { name: 'Meta', roles: ['Data Scientist', 'ML Engineer', 'Research Scientist'] },
    { name: 'Apple', roles: ['ML Engineer', 'Data Scientist', 'AI Researcher'] },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resume Analysis</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Upload your resume for AI-powered analysis and personalized recommendations
        </p>
      </div>

      {/* Upload Section */}
      {!currentResume && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FileUploader
            onUpload={handleUpload}
            isUploading={isLoading}
          />
        </motion.div>
      )}

      {/* Analysis Tabs */}
      {currentResume && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Tabs defaultValue="analysis" className="space-y-4">
            <TabsList>
              <TabsTrigger value="analysis">Resume Analysis</TabsTrigger>
              <TabsTrigger value="gap">Gap Analysis</TabsTrigger>
              <TabsTrigger value="roadmap">Learning Roadmap</TabsTrigger>
            </TabsList>

            <TabsContent value="analysis">
              {analysis ? (
                <ResumeAnalysis analysis={analysis} />
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-gray-600 dark:text-gray-400">
                      Analysis in progress...
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="gap">
              {!gapAnalysis ? (
                <Card>
                  <CardContent className="p-8 space-y-4">
                    <div className="text-center mb-4">
                      <h3 className="text-lg font-medium mb-2">Target Company Analysis</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Select a company to analyze your gaps
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <select
                        value={selectedCompany}
                        onChange={(e) => setSelectedCompany(e.target.value)}
                        className="input"
                      >
                        <option value="">Select Company</option>
                        {companies.map(c => (
                          <option key={c.name} value={c.name}>{c.name}</option>
                        ))}
                      </select>

                      <select
                        value={selectedRole}
                        onChange={(e) => setSelectedRole(e.target.value)}
                        className="input"
                        disabled={!selectedCompany}
                      >
                        <option value="">Select Role</option>
                        {selectedCompany && companies
                          .find(c => c.name === selectedCompany)
                          ?.roles.map(r => (
                            <option key={r} value={r}>{r}</option>
                          ))}
                      </select>
                    </div>

                    <Button
                      onClick={handleGapAnalysis}
                      disabled={!selectedCompany || !selectedRole || isLoading}
                      className="w-full"
                    >
                      Analyze Gaps
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <GapAnalysis
                  analysis={gapAnalysis}
                  targetCompany={selectedCompany}
                  targetRole={selectedRole}
                  onGenerateRoadmap={handleGenerateRoadmap}
                />
              )}
            </TabsContent>

            <TabsContent value="roadmap">
              {roadmap ? (
                <LearningRoadmap roadmap={roadmap} />
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-gray-600 dark:text-gray-400">
                      Complete gap analysis to generate your learning roadmap
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </motion.div>
      )}
    </div>
  )
}