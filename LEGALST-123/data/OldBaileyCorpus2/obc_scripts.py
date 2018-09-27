import re, time, codecs
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from abc import abstractmethod

class BaileyConverter:
    """Abstract super class for converting Old Bailey Corpus xml files
    to pandas dataframe."""

    def __init__(self, xmls):
        self._xmls = xmls

    @property
    @abstractmethod
    def columns(self):
        """A list of the columns for this converter's output."""
        pass

    @abstractmethod
    def to_rows(self, sess):
        """Convert a session of trials into rows for a data frames.
        SESS: the path for one session file
        RETURN: a list of lists, where each nested list represents one row
        with columns as defined in self.columns"""
        pass

    def to_df(self):
        """Convert the data in this converter's sessions to a dataframe."""

        count = 0
        data = []
        t = time.process_time()

        for xml in self._xmls:
            # progress check
            if time.process_time() - t > 30:
                t = time.process_time()
                print('{}% processed'.format(count * 100 / len(self._xmls)))

            with codecs.open('OBO_XML_7-2/sessionsPapers/' + xml, encoding='utf8') as f:
                session = f.read()

            sess_soup = BeautifulSoup(session, 'xml')
            sess_data = self.to_rows(sess_soup)
            data = data + sess_data
            count+=1

        return pd.DataFrame(data, columns=self.columns)

class BaileyChargeConverter(BaileyConverter):
    def __init__(self, xmls):
        super().__init__(xmls)

    @property
    def columns(self):
        """A list of the columns for this converter's output."""
        return ['trial_id', 'trial_date', 'defendant_name', 'defendant_gender',
                'defendant_occupation', 'offence_category', 'offence_subcategory',
                'verdict_category', 'verdict_subcategory', 'punishment_category',
                'punishment_subcategory']

    def to_rows(self, sess_soup):
        """Convert a session of trials into rows for a data frames.
        SESS_SOUP: a BeautifulSoup of one session
        RETURN: a list of lists, where each nested list represents one row
        with columns as defined in self.columns"""

        # empty list to collect trial data
        data = []

        # separate session into trials
        trials = sess_soup('div1', type='trialAccount')

        # iterate through trials
        for trial in trials:
            trial_id = trial['id']
            trial_date = get_tag_val(trial, 'date')

            # get linked defendant, offence, and verdict
            charge_joins = trial('join', result='criminalCharge')

            # skip the trial if there are no linked charges
            if len(charge_joins) == 0:
                pass

            # get linked defendant and punishment
            punishment_joins = trial('join', result='defendantPunishment')
            # get linked people and occupations
            occupation_joins = trial('join', result='persNameOccupation')

            for c_join in charge_joins:
                # get linked ids
                targets = c_join.get('targets').split()
                # check if linked ids include verdict
                if len(targets) == 2:
                    dfdt_id, off_id = targets
                    verd_id = None
                else:
                    dfdt_id, off_id, verd_id = targets

                defendant = trial.find('persName', id=dfdt_id)
                dfdt_name = get_name(defendant)
                dfdt_gender = get_tag_val(defendant, 'gender')

                # default occupation if no occupation joins
                dfdt_occ = None

                #try to match occupations to defendants
                for o_join in occupation_joins:
                    pers_id, occ_id = o_join.get('targets').split()
                    if pers_id == dfdt_id:
                        occupation = trial.find('rs', id=occ_id)
                        dfdt_occ = occupation.get_text()

                offence = trial.find('rs', id=off_id)
                off_categ = get_tag_val(offence, 'offenceCategory')
                off_subcateg =  get_tag_val(offence, 'offenceSubcategory')

                verdict = trial.find('rs', id=verd_id)
                vrd_categ = get_tag_val(verdict, 'verdictCategory')
                vrd_subcateg = get_tag_val(verdict, 'verdictSubcategory')

                # default values if no punishment joins
                pnsh_categ = None
                pnsh_subcateg = None

                #try to match punishments to defendants
                for p_join in punishment_joins:
                    pnsh_pers_id, pnsh_id = p_join.get('targets').split()
                    if pnsh_pers_id == dfdt_id:
                        punishment = trial.find('rs', id=pnsh_id)
                        pnsh_categ = get_tag_val(punishment, 'punishmentCategory')
                        pnsh_subcateg = get_tag_val(punishment, 'punishmentSubcategory')

                # add new row representing the charge
                data = data + [[trial_id, trial_date, dfdt_name, dfdt_gender, dfdt_occ, off_categ, off_subcateg,
                            vrd_categ, vrd_subcateg, pnsh_categ, pnsh_subcateg]]
        return data

class BaileyTranscriptCoverter(BaileyConverter):
    """Convert """
    def __init__(self, xmls):
        super().__init__(xmls)

    @property
    def columns(self):
        """A list of the columns for this converter's output."""

        return ['trial_id', 'trial_date', 'transcript']

    def to_rows(self, sess_soup):
        """Convert a session of trials into rows for a data frames.
        SESS_SOUP: a BeautifulSoup of one session
        RETURN: a list of lists, where each nested list represents one row
        with columns as defined in self.columns"""

        # empty list to collect trial data
        data = []

        # separate session into trials
        trials = sess_soup.find_all('div1', type='trialAccount')

        # iterate through trials
        for trial in trials:

            # get the trial id
            trial_id = trial['id']
            # get trial date
            trial_date = get_tag_val(trial, 'date')

            # get the text
            trial_txt = trial.get_text()
            # remove leading/trailing new lines, extra new lines, extra spaces
            trial_txt = re.sub(r'\n', '', trial_txt)
            trial_txt = re.sub(r'\s\s+', ' ', trial_txt)

            data = data + [[trial_id, trial_date, trial_txt]]
        return data


def get_tag_val(tag_soup, type):
    """Returns the value of tag of type TYPE."""
    if tag_soup is None or tag_soup.find('interp', type=type) is None:
        return None
    else:
        return tag_soup.find('interp', type=type)['value']

def get_name(persName_tag_soup):
    """Returns the string name of the person. If given name or surname
    missing, only returns the extant value. Returns none if no name info
    available."""
    given = get_tag_val(persName_tag_soup, 'given')
    surname = get_tag_val(persName_tag_soup, 'surname')
    if given is not None and surname is not None:
        return given + ' ' + surname
    elif given is not None:
        return given
    elif surname is not None:
        return surname
    else:
        return None
