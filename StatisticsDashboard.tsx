import React from 'react'
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

type Statistic = {
  name: string
  currentValue: number
  previousValue: number
}

const statistics: Statistic[] = [
  { name: 'Total Wins', currentValue: 150, previousValue: 145 },
  { name: 'Total Losses', currentValue: 50, previousValue: 52 },
  { name: 'Assaults Won', currentValue: 80, previousValue: 75 },
  { name: 'Assaults Lost', currentValue: 20, previousValue: 22 },
  { name: 'Defending Battles Won', currentValue: 70, previousValue: 70 },
  { name: 'Defending Battles Lost', currentValue: 30, previousValue: 30 },
  { name: 'Win Rate', currentValue: 75, previousValue: 73 },
  { name: 'Kills', currentValue: 500, previousValue: 480 },
  { name: 'Destroyed Traps', currentValue: 200, previousValue: 190 },
  { name: 'Lost Associates', currentValue: 50, previousValue: 55 },
  { name: 'Lost Traps', currentValue: 100, previousValue: 105 },
  { name: 'Healed Associates', currentValue: 300, previousValue: 290 },
  { name: 'Wounded Enemy Associates', currentValue: 400, previousValue: 380 },
  { name: 'Enemy Turfs Destroyed', currentValue: 30, previousValue: 28 },
  { name: 'Turf Destroyed Times', currentValue: 10, previousValue: 12 },
  { name: 'Eliminated Enemy Influence', currentValue: 1000, previousValue: 950 },
]

export default function StatisticsDashboard() {
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">Battle Statistics Dashboard</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Statistic</TableHead>
              <TableHead>Current Value</TableHead>
              <TableHead>Change Since Last Update</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {statistics.map((stat) => {
              const change = stat.currentValue - stat.previousValue
              const isPositive = change > 0
              const isNeutral = change === 0

              return (
                <TableRow key={stat.name}>
                  <TableCell className="font-medium">{stat.name}</TableCell>
                  <TableCell>{stat.currentValue}</TableCell>
                  <TableCell>
                    <span className={`flex items-center ${isPositive ? 'text-green-600' : isNeutral ? 'text-gray-500' : 'text-red-600'}`}>
                      {isPositive ? (
                        <ArrowUpIcon className="w-4 h-4 mr-1" />
                      ) : isNeutral ? (
                        <span className="w-4 h-4 mr-1">-</span>
                      ) : (
                        <ArrowDownIcon className="w-4 h-4 mr-1" />
                      )}
                      {Math.abs(change)}
                    </span>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}