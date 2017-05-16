import sqlite3
import collections

from feedback import Feedback
from dao.table import Table

class Database:
	dbInstance = None
	@staticmethod
	def instance():
		if Database.dbInstance is None:
			Database.dbInstance = Database.__Database()
		return Database.dbInstance

	class __Database:
		def __init__(self):
			self._db_name = "analyser.db"
			self._db = sqlite3.connect(self._db_name)
			self._initTables()

		def __del__(self):
			self.close()

		def _initTables(self):
			self._feedbacksTable = Table("feedbacks", (
				("id", "integer primary key autoincrement"),
				("content", "text"),
				("value", "integer"),
				("test", "integer"),
			))
			self._createTable(self._feedbacksTable)
			self._unigramsTable = Table("unigrams", (
				("id", "integer primary key autoincrement"),
				("content", "text"),
				("negFrequency", "integer"),
				("posFrequency", "integer")
			))
			self._createTable(self._unigramsTable)
			self._bigramsTable = Table("bigrams", (
				("id", "integer primary key autoincrement"),
				("unigramA", "text"),
				("unigramB", "text"),
				("negFrequency", "integer"),
				("posFrequency", "integer")
			))
			self._createTable(self._bigramsTable)

		def _createTable(self, table, alter = ""):
			columns = ["{0} {1}".format(column.name, column.dataType) for column in table.columns]
			columns = ",".join(columns)
			self._db.execute("create table if not exists {0} ({1}{2});".format(
				table.name,
				columns,
				",{0}".format(alter) if alter else ""
			))
			self._db.commit()

		def insertFeedback(self, feedback):
			columns = ",".join(column.name for column in self._feedbacksTable.columns[1:])
			query = "insert into {0} ({1}) values ({2});".format(
				self._feedbacksTable.name,
				columns,
				",".join(["?"] * (len(self._feedbacksTable.columns) - 1))
			)
			self._db.execute(query, (
				feedback.content,
				feedback.value,
				int(feedback.test)
			))
			self._db.commit()
		
		def selectFeedbacks(self, test = False):
			feedbacks = self._db.execute("select * from {} where test = {};".format(
				self._feedbacksTable.name, int(test)
			))
			for feedback in feedbacks: yield Feedback(*feedback[1:])

		def insertUnigrams(self, unigrams):
			columns = ",".join(column.name for column in self._unigramsTable.columns[1:])
			query = "insert into {0} ({1}) values ({2});".format(
				self._unigramsTable.name,
				columns,
				",".join(["?"] * (len(self._unigramsTable.columns) - 1))
			)
			for unigram in unigrams:
				self._db.execute(query, (
					unigram,
					*unigrams[unigram]
				))
			self._db.commit()
		
		def insertUnigram(self, unigram):
			columns = ",".join(column.name for column in self._unigramsTable.columns[1:])
			query = "insert into {0} ({1}) values ({2});".format(
				self._unigramsTable.name,
				columns,
				",".join(["?"] * (len(self._unigramsTable.columns) - 1))
			)
			self._db.execute(query, unigram)
			self._db.commit()
		
		def insertBigrams(self, bigrams):
			columns = ",".join(column.name for column in self._bigramsTable.columns[1:])
			query = "insert into {0} ({1}) values ({2});".format(
				self._bigramsTable.name,
				columns,
				",".join(["?"] * (len(self._bigramsTable.columns) - 1))
			)
			for X in bigrams:
				for Y in bigrams[X]:
					self._db.execute(query, (X, Y, *bigrams[X][Y]))
			self._db.commit()
		
		def countBigramUsage(self, bigram, posFrequency):
			query = "select sum({}) from {} where %s unigramA = ? and %s unigramB = ?;".format(
				"posFrequency" if posFrequency else "negFrequency",
				self._bigramsTable.name)
			usage = []
			quantors = ("", "not")
			for x in quantors:
				for y in quantors:
					result = self._db.execute(query % (x, y), bigram)
					result, *_ = next(result)
					result = 1 if (result is None or result == 0) else result
					usage.append(result)
			return usage

		def countBigrams(self):
			result = self._db.execute("select sum(negFrequency), sum(posFrequency) from {};".format(
				self._bigramsTable.name
			))
			return next(result)
		
		def selectBigrams(self):
			columns = ",".join(column.name for column in self._bigramsTable.columns[1:])
			result = self._db.execute("select {} from {};".format(
				columns,
				self._bigramsTable.name
			))
			yield from result

		def countFeedbacksByClass(self, value):
			result = self._db.execute("select count(*) from {} where value = {};".format(
				self._feedbacksTable.name, int(value)
			))
			result, *_ = next(result)
			return result

		def countUniqueUnigrams(self):
			result = self._db.execute("select count(*) from {};".format(
				self._unigramsTable.name
			))
			result, *_ = next(result)
			return result

		def countUnigrams(self):
			result = self._db.execute("select sum(negFrequency), sum(posFrequency) from {};".format(
				self._unigramsTable.name
			))
			return next(result)

		def selectUnigramFrequencies(self, unigram):
			result = self._db.execute("select negFrequency, posFrequency from {} where content = \"{}\";".format(
				self._unigramsTable.name, unigram
			))
			try: return next(result)
			except StopIteration: return (0, 0)

		def selectUnigramUsage(self, unigram, value):
			return self._selectUnigramUsage("posFrequency" if value else "negFrequency", unigram)

		def _selectUnigramUsage(self, value, unigram):
			result = self._db.execute("select {} from {} where content = \"{}\";".format(
				value, self._unigramsTable.name, unigram
			))
			try:
				result, *_ = next(result)
				return result
			except StopIteration:
				return 0
		
		def deleteUnigrams(self):
			query = "delete from {}".format(self._unigramsTable.name)
			self._db.execute(query)
			self._db.commit()
		
		def deleteBigrams(self):
			query = "delete from {}".format(self._bigramsTable.name)
			self._db.execute(query)
			self._db.commit()

		def close(self):
			self._db.close()