import {Request, Response, NextFunction} from 'express'
import {appendFileSync} from 'fs'
import path from 'path'

const EXPERIMENTER_FOLDER = process.env.EXPPATH
  ? path.resolve(process.env.EXPPATH)
  : path.resolve('./')

export const logResult = (req: Request, res: Response, next: NextFunction) => {
  const {uid, condition, docId, decision, completionTime} = req.body
  const filename = path.join(EXPERIMENTER_FOLDER, `ind_${uid}.csv`)
  const timestamp = Date.now()

  const row = `${uid},${condition},${docId},${decision},${completionTime},${timestamp}\n`
  appendFileSync(filename, row)

  return res.status(200).send({message: 'ok'})
}
