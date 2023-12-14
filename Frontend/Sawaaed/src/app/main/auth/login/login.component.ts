import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { Router } from '@angular/router';
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ButtonModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  constructor(private route: Router){}

  goToPubPage() {
    this.route.navigate(['/publisher']);
  }
  goToSubPage() {
    this.route.navigate(['/subscriber']);
  }

}
