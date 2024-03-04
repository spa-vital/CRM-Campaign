from django.db import models
from django.contrib.auth.models import User
from team.models import Team
from product.models import Product
# Create your models here.

class LeadSource(models.Model):
    name = models.CharField(max_length=100, blank=True, null= True)
    description = models.CharField(max_length=200, blank=True, null= True)

    def __str__(self):
        return self.name
      
    class Meta:
        ordering = ('name',)
    

class Lead(models.Model):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CHOICES_PRIORITY = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High')
    )
    NEW = 'new'
    CONTACTED = 'contacted'
    QUA = 'qualified'
    UNACTIONED = 'unactioned'
    UN = 'unqualified'
    CHOICES_STATUS = (
        (NEW, 'New'),
        (CONTACTED, 'Contacted'),
        (QUA, 'Qualified'),
        (UN, 'Unqualified'),
        (UNACTIONED, 'Unactioned'),
    )
    team = models.ForeignKey(Team, related_name='leads', on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=CHOICES_PRIORITY, default=MEDIUM)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default=NEW)
    converted_to_client = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='leads', on_delete=models.CASCADE,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True, null= True)
    product_line = models.ForeignKey(Product, related_name='leads', on_delete=models.CASCADE,default=1)
    company = models.CharField(max_length=100, blank=True, null= True)
    job = models.CharField(max_length=100, blank=True, null= True)
    lead_source = models.ForeignKey(LeadSource,related_name='leads', on_delete=models.CASCADE,default=1)
    
    # @property
    # def full_name(self):
    #     return f"{self.first_name} {self.last_name}"

    # def  __str__(self):
    #     return self.full_name

    def __str__(self):
        return self.name
      
    class Meta:
        ordering = ('name',)
        # # Định nghĩa constraints
        # constraints = [
        #     models.CheckConstraint(
        #         name="valid_proprity",
        #         check=models.Q(Proprity__in=[choice[0] for choice in PRIORITY_CHOICES]),
        #     ),
        # ]


        # constraints = [
        #     models.CheckConstraint(
        #         name="valid_status",
        #         check=models.Q(Status__in=[choice[0] for choice in STATUS_CHOICES]),
        #     ),
        # ]

    

class LeadFile(models.Model):
    team = models.ForeignKey(Team, related_name='lead_files', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, related_name= 'files', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='lead_files', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='leadfiles')

    def __str__(self):
        return self.created_by.username
    
    

class Comment(models.Model):
    team = models.ForeignKey(Team, related_name='lead_comments', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, related_name= 'comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='lead_comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True)

    def __str__(self):
        return self.created_by.username


    


