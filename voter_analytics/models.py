from django.db import models

# Create your models here.
class Voter(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    st_num = models.TextField()     # street number
    st_name = models.TextField()    # street name
    ap_num = models.TextField(blank=True)     # apartment number
    zip_code = models.IntegerField(blank=True)
    dob = models.DateField()    # date of birth
    dor = models.DateField()    # date of registration
    party_affil = models.CharField(max_length=2)
    precinct_num = models.TextField(blank=True)

    v20state = models.TextField()
    v21town = models.TextField()
    v21primary = models.TextField()
    v22general = models.TextField()
    v23town = models.TextField()

    def __str__(self):
        '''Return a string representation of this model instance.'''
        return f'{self.first_name} {self.last_name} ({self.st_name}, {self.zip_code}), {self.dob}'
    def voter_score(self):
        '''Return the number of elections this voter participated in.'''
        elections = [self.v20state, self.v21town, self.v21primary, self.v22general, self.v23town]
        return sum(1 for e in elections if e.strip().upper() == 'TRUE')


def load_data():
    '''Function to load data records from CSV file into Django model instances.'''
 
 
    filename = '/Users/alexcobb/Desktop/django/voter_analytics/newton_voters.csv'
    f = open(filename)
    f.readline() # discard headers
 
    for line in f:
        fields = line.strip().split(',')
        print(f'fields={fields}')
        try:
            result = Voter(
                            first_name=fields[1],
                            last_name=fields[2],
                            st_num = fields[3],
                            st_name = fields[4],
                            ap_num = fields[5],
                            
                            zip_code = fields[6],
                            dob = fields[7],
    
                            dor = fields[8],
                            party_affil = fields[9],
                            precinct_num = fields[10],
                        
                            v20state = fields[11],
                            v21town = fields[12],
                            v21primary = fields[13],
                            v22general = fields[14],
                            v23town = fields[15],
                                )
            result.save()
        except Exception as e:
            print(f'Skipped: {fields}, Error: {e}')
    print(f'Done. Created {len(Voter.objects.all())} Results.')