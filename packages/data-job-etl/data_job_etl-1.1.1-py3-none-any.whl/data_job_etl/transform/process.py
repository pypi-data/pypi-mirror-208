import pandas as pd
import re

from data_job_etl.build_technos import TechnoBuilder


class Processor:

    def process_technos(self, jobs):
        """
        Add columns to a dataframe with technology names from a text.
        """
        jobs = self.add_stack(jobs)
        jobs = self.expand_stack(jobs)
        return jobs

    def pivot_technos(self, jobs):
        """
        Keep technology names in a single column. Format for Tableau.
        """
        jobs = self.melt_technos(jobs)
        jobs = self.clean_pivot(jobs)
        return jobs

    def add_stack(self, jobs):
        """
        Add new stack column containing a list of technologies.
        """
        jobs['stack'] = jobs['text'].apply(lambda x: self.extract_technos(x))
        return jobs

    @staticmethod
    def extract_technos(text):
        """
        Identify and extract list of technology names.
        """
        technos = TechnoBuilder().build_all_technos()
        words = re.split(r'\W+', text)
        technos_in_text = {w for w in words if w in technos}
        return list(set(technos_in_text))

    @staticmethod
    def expand_stack(jobs):
        """
        Expand the stack column in as many columns as there are elements.
        """
        technos = pd.DataFrame(jobs['stack'].to_list())
        expanded = pd.merge(jobs, technos, left_index=True, right_index=True)
        return expanded

    @staticmethod
    def melt_technos(jobs):
        """ 
        Melt dataframe to have one technology per row (for usage in Tableau). 
        """
        unpivotted_columns = ['id', 'url', 'title', 'company', 'location', 'type', 'industry', 'remote', 'created_at',
                              'text', 'stack', 'size', 'education', 'experience']
        jobs = pd.melt(jobs, id_vars=unpivotted_columns).sort_values(by=['company', 'created_at', 'title'])
        jobs.reset_index(drop=True, inplace=True)
        return jobs

    @staticmethod
    def clean_pivot(jobs):
        """
        Delete unrelevant columns and rows.
        """
        jobs['technos'] = jobs['value']
        jobs.drop(['variable', 'stack', 'value'], axis=1, inplace=True)
        jobs.dropna(subset='technos', inplace=True)
        return jobs.reset_index(drop=True)
