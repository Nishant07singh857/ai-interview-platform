import { redirect } from 'next/navigation'

export default function PracticeResultsRedirect({
  params,
}: {
  params: { sessionId: string }
}) {
  redirect(`/practice/session/results/${params.sessionId}`)
}
